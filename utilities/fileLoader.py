from pathlib import Path
import rdflib

class RDFFileLoader:

    def __init__(self, encoding = "utf-8"):
        self.encoding = encoding

    @staticmethod
    def is_ttl(path: Path):
        return path.suffix.lower() == ".ttl"

    def load_text(self, path: Path) -> str:
        with path.open("r", encoding=self.encoding) as f:
            return f.read()

    def load_graph(self, path: Path, graph_format = "turtle"):
        text = self.load_text(path)
        graph = rdflib.Graph()
        graph.parse(data=text, format=graph_format)
        return graph