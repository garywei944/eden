import atexit
import importlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Generator, Literal

import networkx as nx
from dagviz import visualize_dag

from eden.args import Args
from eden.context import Context
from eden.esh import esh as sh
from evakit.singleton import Singleton

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

    exit_hooks: list[Callable[[], None]] = field(default_factory=list)

    _graph: nx.DiGraph = field(default_factory=nx.DiGraph)
    _modules: dict[str, object] = field(default_factory=dict)

    def __post_init__(self):
        self.sudo = self.ctx.has_sudo and not self.args.standalone

        if self.ctx.os_id in ["ubuntu", "debian"]:
            self.pkgmgr = "apt"
        elif self.ctx.is_arch:
            self.pkgmgr = "paru"
        else:
            raise RuntimeError(f"Unsupported OS: {self.ctx.os_id}")

        def _exit_hook():
            logger.info("Running Eva exit hooks...")
            for hook in self.exit_hooks:
                try:
                    hook()
                except Exception as e:
                    logger.error("Error running exit hook: %s", e)

        atexit.register(_exit_hook)

    def build_graph(self):
        stack = self.targets.copy() + ["pkgmgr"]
        optdepends: list[tuple[str, str]] = []

        while stack:
            target = stack.pop()
            try:
                module = importlib.import_module(f"eden.species.{target}")
            except ModuleNotFoundError as e:
                # check it it's because the module doesn't exist, not because of an import error
                # inside the module
                if e.name != f"eden.species.{target}":
                    raise

                # self._graph.add_node(target)
                self._graph.add_edge("pkgmgr", target)
                continue

            if getattr(module, "requires_pkgmgr", True):
                self._graph.add_edge("pkgmgr", target)

            self._modules[target] = module
            deps = getattr(module, "depends", [])
            for dep in deps:
                if dep not in self._graph.nodes:
                    stack.append(dep)
                self._graph.add_edge(dep, target)
            opt_deps = getattr(module, "optdepends", [])
            for dep in opt_deps:
                optdepends.append((dep, target))
        logger.info("Eva initialized with targets: %s", self.targets)

        # add optional dependencies only if they are already in the graph
        for dep, target in optdepends:
            if dep in self._graph.nodes:
                self._graph.add_edge(dep, target)

        if not nx.is_directed_acyclic_graph(self._graph):
            logger.warning("All cycles in the dependency graph:\n%s", list(nx.simple_cycles(self._graph)))
            raise RuntimeError("Dependency graph has cycles!")

        logger.debug("Dependency graph edges:\n%s", visualize_dag(self._graph, round_angle=True))

    def plan(self) -> Generator[list[str], None, None]:
        for pkgs in nx.topological_generations(self._graph):
            yield list(pkgs)

    def execute(self, targets: list[str]):
        logger.info("=" * 80)

        # exclude targets in args.excludes
        original_targets = list(targets)
        targets = [t for t in original_targets if t not in self.args.excludes]
        excluded = [t for t in original_targets if t in self.args.excludes]
        if excluded:
            logger.warning("Excluding targets: %s", excluded)

        logger.info("Executing installation batch: %s", targets)
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

            # get the package manager for this module
            if hasattr(module, "pkgmgr"):
                pkgmgr = getattr(module, "pkgmgr")
            elif self.sudo:
                pkgmgr = self.pkgmgr
            else:
                # default to use cargo if no sudo
                pkgmgr = "cargo"

            if module is None:
                pkg_batches[pkgmgr].append(target)
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

                pkg = getattr(module, "pkgname", target)
                if isinstance(pkg, list):
                    pkg_batches[pkgmgr].extend(pkg)
                elif pkg is not None:
                    pkg_batches[pkgmgr].append(pkg)

        for pkgmgr, pkgs in pkg_batches.items():
            pkgs = list(set(pkgs))  # deduplicate
            logger.info("Installing packages with %s: %s", pkgmgr, pkgs)
            if not self.args.dry_run:
                if pkgmgr == "apt":
                    sh.sudo("apt-get", "install", "-y", *pkgs, _tty_out=False)
                elif pkgmgr == "pacman":
                    sh.sudo.pacman("-S", "--noconfirm", "--needed", *pkgs)
                elif pkgmgr in ["pacman", "yay", "paru"]:
                    sh.Command(pkgmgr)(["-S", "--noconfirm", "--needed", *pkgs])
                elif pkgmgr == "cargo":
                    sh.cargo.install(*pkgs)
                else:
                    raise RuntimeError(f"Unsupported package manager: {pkgmgr}")

        if not self.sudo:
            if "apt" in pkg_batches:
                raise RuntimeError("Cannot install apt packages without sudo!")

        # 3. run all post_install hooks
        for target in targets:
            module = self._modules.get(target)
            if module and hasattr(module, "post_install"):
                if not self.args.dry_run:
                    getattr(module, "post_install")()
