from abc import ABC, abstractmethod
from typing import Any, Dict

class IIoTPlatformExtractor(ABC):
    def __init__(self, graphdb_url: str, repository: str):
        if not graphdb_url:
            raise ValueError("GraphDB URL is required")
        if not repository:
            raise ValueError("Repository is required")
        self.graphdb_url = graphdb_url
        self.repository = repository

    @abstractmethod
    def extract_entities_from_graphdb(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def extract_entities_relationships(self) -> Dict[str, Any]:
        raise NotImplementedError