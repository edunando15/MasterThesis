from abc import ABC, abstractmethod
from typing import Any, Dict
from adapters.adapter import IAdapter

class IDeployer(ABC):

    def __init__(self, adapter: IAdapter, extracted_entities: Dict[str, Any]):
        if not adapter:
            raise ValueError("Adapter is required")
        if not extracted_entities:
            raise ValueError("Extracted entities are required")
        self.adapter = adapter
        self.assets = extracted_entities.get("assets", [])
        self.devices = extracted_entities.get("devices", [])
        self.relationships = extracted_entities.get("relationships", [])
        self.devices_ids = []
        self.assets_ids = []

    @abstractmethod
    def deploy(self, username: str, password: str):
        raise NotImplementedError
