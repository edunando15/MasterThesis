from utilities.fileLoader import RDFFileLoader
from pathlib import Path

path = Path("../data/iot_platform_ontology.ttl")
rdf_reader = RDFFileLoader()
graph = rdf_reader.load_graph(path)
print(graph)