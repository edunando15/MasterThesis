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
        self.observations = extracted_entities.get("observations", [])
        self.relationships = extracted_entities.get("relationships", [])
        self.devices_ids = []
        self.assets_ids = []

    def _is_aggregated_sensor(self, device: Dict[str, Any]) -> bool:
        is_aggregated = device.get("isAggregatedSensor", "")
        return str(is_aggregated).strip().lower() == "true"

    def _compute_ignored_sub_sensors(self) -> set[str]:
        device_map = {d["subject"]: d for d in self.devices if "subject" in d}
        ignored = set()
        for rel in self.relationships:
            rel_name = rel.get("relation", "")
            if "hasSubSensor" in rel_name:
                parent_uri = rel.get("subject")
                child_uri = rel.get("object")
                parent = device_map.get(parent_uri)
                if parent and self._is_aggregated_sensor(parent):
                    ignored.add(child_uri)
        return ignored

    @abstractmethod
    def deploy(self, username: str, password: str) -> Dict[Any, Any]:
        raise NotImplementedError
