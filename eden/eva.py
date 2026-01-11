import importlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Generator, Literal

import networkx as nx
import sh
from dagviz import visualize_dag

from eden.args import Args
from eden.context import Context
from eden.utils.misc import command_exists
from eden.utils.singleton import Singleton

logger = logging.getLogger(__name__)


@dataclass
class Eva(Singleton):
    args: Args
    ctx: Context

    # targets must form an acyclic graph, so we can topologically sort them
    # and install everything in iterations.
    targets: list[str]

    pkgmgr: Literal["apt", "pacman", "yay", "paru"] = field(init=False)
    sudo: bool = field(init=False)

    _graph: nx.DiGraph = field(default_factory=nx.DiGraph)
    _modules: dict[str, object] = field(default_factory=dict)

    def __post_init__(self):
        self.sudo = self.ctx.has_sudo and not self.args.standalone

        if self.ctx.os_id in ["ubuntu", "debian"]:
            self.pkgmgr = "apt"
        elif self.ctx.os_id == "arch":
            self.pkgmgr = "paru"
        else:
            raise RuntimeError(f"Unsupported OS: {self.ctx.os_id}")

    def ensure_sudo(self):
        if not self.sudo:
            return
        if self.ctx.is_root and not command_exists("sudo"):
            logger.info("Installing sudo as root")
            if self.pkgmgr == "apt":
                sh.apt.install("-y", "sudo")
            elif self.ctx.os_id == "arch":
                sh.pacman("-Syu", "--noconfirm", "sudo")
            else:
                raise RuntimeError(f"Unsupported OS: {self.ctx.os_id}")

    def build_graph(self):
        stack = self.targets.copy()

        while stack:
            target = stack.pop()
            try:
                module = importlib.import_module(f"eden.species.{target}")
            except ModuleNotFoundError:
                self._graph.add_node(target)
                continue
            self._modules[target] = module
            deps = getattr(module, "depends", [])
            for dep in deps:
                if dep not in self._graph.nodes:
                    stack.append(dep)
                self._graph.add_edge(dep, target)
        logger.info("Eva initialized with targets: %s", self.targets)

        if not nx.is_directed_acyclic_graph(self._graph):
            raise RuntimeError("Dependency graph has cycles!")

        logger.debug("Dependency graph edges:\n%s", visualize_dag(self._graph, round_angle=True))

    def plan(self) -> Generator[list[str], None, None]:
        for pkgs in nx.topological_generations(self._graph):
            logger.info("Next installation batch: %s", pkgs)
            yield list(pkgs)

    def execute(self, targets: list[str]):
        logger.info("=" * 80)
        # 1. run all pre_install hooks
        for target in targets:
            module = self._modules.get(target)
            if module and hasattr(module, "pre_install"):
                logger.info("Running pre_install hook for %s", target)
                if not self.args.dry_run:
                    getattr(module, "pre_install")()

        # 2. collect all packages manager packages, so we can batch install them
        pkg_batches = defaultdict(list)
        for target in targets:
            # 1) add package to the default package manager installation batch
            module = self._modules.get(target)
            if module is None:
                pkg_batches[self.pkgmgr].append(target)
                continue
            # 2) skip if the package is a meta package
            if getattr(module, "is_meta_pkg", False):
                logger.debug("Skipping meta package %s", target)
                continue
            # 3) run the install hook if it exists
            if hasattr(module, "install"):
                logger.info("Running install hook for %s", target)
                if not self.args.dry_run:
                    getattr(module, "install")()
            else:
                pkg_batches[getattr(module, "pkgmgr", self.pkgmgr)].append(
                    getattr(module, "pkgname", target)
                )
        logger.info("Package installation batches: %s", dict(pkg_batches))

        if not self.sudo:
            if "apt" in pkg_batches:
                raise RuntimeError("Cannot install apt packages without sudo!")

        # 3. run all post_install hooks
        for target in targets:
            module = self._modules.get(target)
            if module and hasattr(module, "post_install"):
                logger.info("Running post_install hook for %s", target)
                if not self.args.dry_run:
                    getattr(module, "post_install")()
