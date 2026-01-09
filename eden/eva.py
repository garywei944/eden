import importlib
import logging

import attrs
import networkx as nx
from dagviz import visualize_dag

from eden.utils.singleton import Singleton

logger = logging.getLogger(__name__)


@attrs.define
class Eva(Singleton):
    # targets must form an acyclic graph, so we can topologically sort them
    # and install everything in iterations.
    targets: list[str]

    _graph: nx.DiGraph = attrs.field(factory=nx.DiGraph)
    _modules: dict[str, object] = attrs.field(factory=dict)

    def __attrs_post_init__(self):
        for target in self.targets:
            module = importlib.import_module(f"eden.species.{target}")
            self._modules[target] = module
            deps = getattr(module, "depends", [])
            for dep in deps:
                self._graph.add_edge(dep, target)
        logger.info("Eva initialized with targets: %s", self.targets)
        logger.debug("Dependency graph edges:\n%s", visualize_dag(self._graph))
