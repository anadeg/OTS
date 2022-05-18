import networkx as nx


class UndirectedGraph:
    def __init__(self, name: str):
        self.graph = nx.Graph()
        self.name = name
