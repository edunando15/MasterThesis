from .deployer import IDeployer
from adapters.thingsboardAdapter import ThingsboardAdapter
from typing import Any, Dict, Optional
from adapters.type import Type

class ThingsboardDeployer(IDeployer):

    def __init__(self, adapter: ThingsboardAdapter, extracted_entities: Dict[str, Any]):
        super().__init__(adapter, extracted_entities)
        self._entity_registry = {}

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

    def _find_observation_for_device(self, device_uri: str) -> Optional[str]:
        observations = []
        for rel in self.relationships:
            if "madeBySensor" in rel.get("relation", ""):
                if rel.get("object") == device_uri:
                    obs_uri = rel.get("subject")
                    if obs_uri and obs_uri not in observations:
                        observations.append(obs_uri)
        return ", ".join(observations) if observations else None

    def _deploy_assets(self):
        for asset in self.assets:
            uri = asset.get("subject")
            if not uri:
                continue

            tb_id = self.adapter.add_zone(uri)
            if tb_id:
                self.assets_ids.append(tb_id)
                self._entity_registry[uri] = {"id": tb_id, "type": Type.ASSET}

    def _deploy_devices(self):
        ignored_devices = self._compute_ignored_sub_sensors()
        for device in self.devices:
            uri = device.get("subject")
            if not uri or uri in ignored_devices:
                continue

            observation_uri = self._find_observation_for_device(uri)
            description = None
            if observation_uri:
                description = observation_uri

            tb_id = self.adapter.add_device(uri, description)
            if tb_id:
                self.devices_ids.append(tb_id)
                self._entity_registry[uri] = {"id": tb_id, "type": Type.DEVICE}

    def _deploy_relationships(self):
        for rel in self.relationships:
            subject_uri = rel.get("subject")
            object_uri = rel.get("object")

            parent = self._entity_registry.get(subject_uri)
            child = self._entity_registry.get(object_uri)

            if parent and child:
                self.adapter.add_relationship(
                    parent=parent["id"],
                    parent_type=parent["type"],
                    child=child["id"],
                    child_type=child["type"]
                )


    def deploy(self, username: str, password: str) -> Dict[Any, Any]:
        self.adapter.authenticate(username, password)
        self._deploy_assets()
        self._deploy_devices()
        self._deploy_relationships()
        return self._entity_registry
