import os
import requests
from typing import Any, Dict, List, Optional, Sequence
from dotenv import load_dotenv
from extractors.iotPlatformExtractor import IIoTPlatformExtractor

load_dotenv()

class EntityExtractor(IIoTPlatformExtractor):

    def __init__(self, graphdb_url: str, repository: str):
        super().__init__(graphdb_url, repository)
        self.zone_types = ["bot:Zone", "bop:Site", "bot:Building", "bop:storey", "bot:Space"]
        self.device_types = ["iotpo:Device"]
        self.structural_relations = ["bot:hasBuilding", "bot:hasStorey", "bot:hasSpace"]

        self.relationships_filter = [
                "bot:containsElement",
                "bop:hasSubSensor",
            ]

        self.raw_results: List[Dict[str, Any]] = []
        self.assets: List[Dict[str, str]] = []
        self.devices: List[Dict[str, str]] = []
        self.relationships: List[Dict[str, str]] = []

    def _build_prefix(self, reference: str) -> str:
        return f"PREFIX {os.getenv(reference)}"

    def extract_entities_from_graphdb(self) -> str:
        zone_types = ", ".join(self.zone_types)
        device_types = ", ".join(self.device_types)
        all_types = ", ".join(self.zone_types + self.device_types)
        structural_rels = ", ".join(self.structural_relations)

        return f"""
                {self._build_prefix("BOT")}
                {self._build_prefix("IOTPO")}
                {self._build_prefix("BOP")} 

                SELECT ?subject ?type ?relation ?object
                WHERE {{
                    {{
                        # Extract all target entities
                        ?subject a ?type .
                        FILTER(?type IN ({all_types}))
                    }}
                    UNION
                    {{
                        # Constraint: Zone -> Structural -> Zone
                        ?subject ?relation ?object .
                        FILTER(?relation IN ({structural_rels}))

                        ?subject a ?subType .
                        FILTER(?subType IN ({zone_types}))

                        ?object a ?objType .
                        FILTER(?objType IN ({zone_types}))
                    }}
                    UNION
                    {{
                        # Constraint: Zone -> containsElement -> Device ONLY
                        ?subject ?relation ?object .
                        FILTER(?relation = {self.relationships_filter[0]})

                        ?subject a ?subType .
                        FILTER(?subType IN ({zone_types}))

                        ?object a ?objType .
                        FILTER(?objType IN ({device_types}))
                    }}
                    UNION
                    {{
                        # Constraint: Device -> hasSubSensor -> Device
                        ?subject ?relation ?object .
                        FILTER(?relation = {self.relationships_filter[1]})

                        ?subject a ?subType .
                        FILTER(?subType IN ({device_types}))

                        ?object a ?objType .
                        FILTER(?objType IN ({device_types}))
                    }}
                }}
                """

    def _query_graphdb(self, sparql: str) -> List[Dict[str, Any]]:
        response = requests.post(
            f"{self.graphdb_url}/repositories/{self.repository}",
            data={"query": sparql},
            headers={"Accept": "application/sparql-results+json"},
            timeout=30,
        )
        response.raise_for_status()

        return response.json()

    @staticmethod
    def _binding_value(binding: Dict[str, Any], var_name: str) -> Optional[str]:
        value = binding.get(var_name)
        if not value:
            return None
        return value.get("value")

    def extract_entities_relationships(self) -> Dict[str, Any]:
        sparql = self.extract_entities_from_graphdb()
        self.raw_results = self._query_graphdb(sparql)
        self.devices = []
        self.assets = []
        self.relationships = []
        bindings = self.raw_results.get("results", {}).get("bindings", [])
        for row in bindings:
            subject = self._binding_value(row, "subject")
            type_name = self._binding_value(row, "type")
            relation = self._binding_value(row, "relation")
            obj = self._binding_value(row, "object")

            if subject and type_name and relation is None and obj is None:
                if type_name.endswith("Device"):
                    self.devices.append({"subject": subject, "type": type_name})
                else:
                    self.assets.append({"subject": subject, "type": type_name})
            elif subject and relation and obj:
                self.relationships.append(
                    {
                        "subject": subject,
                        "relation": relation,
                        "object": obj,
                    }
                )

        return {
            "assets": self.assets,
            "devices": self.devices,
            "relationships": self.relationships,
            "raw_results": self.raw_results,
        }