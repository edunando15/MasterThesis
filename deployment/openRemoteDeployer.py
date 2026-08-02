from adapters.adapter import IAdapter
from .deployer import IDeployer
from typing import Any, Dict
from adapters.type import Type

class OpenRemoteDeployer(IDeployer):
    def __init__(self, adapter: IAdapter, extracted_entities: Dict[str, Any]):
        super().__init__(adapter, extracted_entities)
        self._entity_registry = {}

    def _find_observation_for_device(self, device_uri: str) -> list[str]:
        observations = set()
        for rel in self.relationships:
            if "madeBySensor" in rel.get("relation", ""):
                if rel.get("object") == device_uri:
                    obs_uri = rel.get("subject")
                    if obs_uri and obs_uri not in observations:
                        observations.add(obs_uri.lower())
        return list(observations)

    def _deploy_entities_hierarchically(self):
        pending = {}
        child_to_parent = {}

        for rel in self.relationships:
            rel_name = rel.get("relation", "").lower()
            if "contains" in rel_name or "hassubsensor" in rel_name:
                child_to_parent[rel.get("object")] = rel.get("subject")

        for asset in self.assets:
            if uri := asset.get("subject"):
                pending[uri] = {"data": asset, "category": "ASSET"}

        ignored_devices = self._compute_ignored_sub_sensors()
        for device in self.devices:
            if (uri := device.get("subject")) and uri not in ignored_devices:
                pending[uri] = {"data": device, "category": "DEVICE"}

        while pending:
            deployed_in_this_pass = []

            for uri, info in pending.items():
                parent_uri = child_to_parent.get(uri)

                if not parent_uri or parent_uri in self._entity_registry:
                    parent_id = self._entity_registry[parent_uri]["id"] if parent_uri in self._entity_registry else None
                    element_id = None
                    device_obs = []

                    if info["category"] == "ASSET":
                        element_id = self.adapter.add_zone(
                            uri,
                            has_type=info["data"].get("hasType"),
                            parent=parent_id
                        )
                        ent_type = Type.ASSET
                        if element_id:
                            self.assets_ids.append(element_id)

                    elif info["category"] == "DEVICE":
                        device_obs = self._find_observation_for_device(uri)
                        element_id = self.adapter.add_device(
                            uri,
                            attributes=device_obs,
                            has_id=info["data"].get("hasId"),
                            parent=parent_id
                        )
                        ent_type = Type.DEVICE
                        if element_id:
                            self.devices_ids.append(element_id)

                    if element_id:
                        self._entity_registry[uri] = {"id": element_id, "type": ent_type}
                        if info["category"] == "DEVICE":
                            self._entity_registry[uri]["observations"] = device_obs
                    deployed_in_this_pass.append(uri)

            if not deployed_in_this_pass:
                break

            for uri in deployed_in_this_pass:
                del pending[uri]


    def deploy(self, username: str, password: str) -> Dict[Any, Any]:
        self.adapter.authenticate(username, password)
        self._deploy_entities_hierarchically()
        return self._entity_registry
