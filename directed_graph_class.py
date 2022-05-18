import networkx as nx


class DirectedGraph:
    def __init__(self, name: str):
        self.graph = nx.DiGraph()
        self.name = name
