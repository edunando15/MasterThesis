from .deployer import IDeployer
from adapters.thingsboardAdapter import ThingsboardAdapter
from typing import Any, Dict
from adapters.type import Type

class ThingsboardDeployer(IDeployer):

    def __init__(self, adapter: ThingsboardAdapter, extracted_entities: Dict[str, Any]):
        super().__init__(adapter, extracted_entities)
        self._entity_registry = {}

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
        for device in self.devices:
            uri = device.get("subject")
            if not uri:
                continue

            tb_id = self.adapter.add_device(uri)
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


    def deploy(self, username: str, password: str):
        self.adapter.authenticate(username, password)
        self._deploy_assets()
        self._deploy_devices()
        self._deploy_relationships()
