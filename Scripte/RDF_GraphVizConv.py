from bs4 import BeautifulSoup


class Node:
    def __init__(self, id, label):
        self.id = id
        self.label = label
        self.shape = "ellipse"

    def __str__(self):
        return f'"{self.id}" [label="{self.label}",shape={self.shape}];'


class Edge:
    def __init__(self, start, end, label):
        self.start = start
        self.end = end
        self.label = label

    def __str__(self):
        return f'"Rmigr:{self.start}" -> "Rmigr:{self.end}" [{self.label}];\n'


class Graph(object):
    def __init__(self):
        self.nodes = []
        self.edges = []

    def _add_node(self, node: Node):
        self.nodes.append(node)

    def _add_edge(self, edf: Edge):
        self.edges.append(edf)

    def read_rdf(self, rdf_file):
        with open(rdf_file, 'r', encoding="utf-8") as f:
            text = f.read()
        soup = BeautifulSoup(text, "xml")
        nodes = soup.find_all("rdf:Description")
        for node in nodes:
            self._add_node(Node(node["about"], node["name"]))

            for edge in node.children:
                self._add_edge(Edge(node["about"], edge["resource"], edge.name))

    def __str__(self):
        e = "".join([edge.__str__() for edge in self.edges])
        n = "".join([node.__str__() for node in self.nodes])
        start = f''' charset="utf-8"; {e} {n}'''
        return f"digraph {start}"


graph = Graph()
graph.read_rdf("Bornschlegel.rdf")
print(graph)
