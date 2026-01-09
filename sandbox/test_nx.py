import networkx as nx
from dagviz import visualize_dag

G = nx.DiGraph()

# low-level prerequisites
G.add_edge("sudo", "apt")
G.add_edge("sudo", "curl")

# language runtimes
G.add_edge("curl", "rust")
G.add_edge("rust", "cargo")

# core tools
G.add_edge("cargo", "fd")
G.add_edge("cargo", "bat")
G.add_edge("cargo", "ripgrep")
G.add_edge("cargo", "zoxide")

# other branches
G.add_edge("apt", "git")
G.add_edge("apt", "tmux")

# user tools depending on git
G.add_edge("git", "lazygit")

# cross dependency
G.add_edge("cargo", "broot")
G.add_edge("git", "broot")

G.add_node("htop")  # standalone node

print(visualize_dag(G))
