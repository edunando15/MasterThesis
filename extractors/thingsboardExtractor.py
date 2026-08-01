import os
import requests
from typing import Any, Dict, List, Optional, Sequence
from dotenv import load_dotenv
from extractors.iotPlatformExtractor import IIoTPlatformExtractor

load_dotenv()

class ThingsboardExtractor(IIoTPlatformExtractor):

    def __init__(self, graphdb_url: str, repository: str):
        super().__init__(graphdb_url, repository)
        self.zone_types = ["thingsboard:Asset"]
        self.device_types = ["thingsboard:Device"]
        self.observation_types = ["sosa:Observation"]
        self.structural_relations = ["thingsboard:containsAsset"]

        self.relationships_filter = [
                "thingsboard:containsDevice",
                "bop:hasSubSensor",
                "sosa:madeBySensor",
                "iotpo:isAggregatedSensor",
                "iotpo:hasId",
            ]

        self.raw_results: List[Dict[str, Any]] = []
        self.assets: List[Dict[str, str]] = []
        self.devices: List[Dict[str, str]] = []
        self.observations: List[Dict[str, str]] = []
        self.relationships: List[Dict[str, str]] = []

    def _build_prefix(self, reference: str) -> str:
        return f"PREFIX {os.getenv(reference)}"

    def extract_entities_from_graphdb(self) -> str:
        zone_types = ", ".join(self.zone_types)
        device_types = ", ".join(self.device_types)
        all_types = ", ".join(self.zone_types + self.device_types + self.observation_types)
        structural_rels = ", ".join(self.structural_relations)

        return f"""
                {self._build_prefix("BOT")}
                {self._build_prefix("IOTPO")}
                {self._build_prefix("BOP")} 
                {self._build_prefix("SOSA")}
                {self._build_prefix("THINGSBOARD")}

                SELECT ?subject ?type ?relation ?object ?isAggregatedSensor ?hasId
                WHERE {{
                    {{
                        # Extract all target entities
                        ?subject a ?type .
                        FILTER(?type IN ({all_types}))
                        OPTIONAL {{ ?subject {self.relationships_filter[3]} ?isAggregatedSensor }}
                        OPTIONAL {{ ?subject {self.relationships_filter[4]} ?hasId . }}
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
                    UNION
                    {{
                        # Constraint: Observation -> sosa:madeBySensor -> Device (sensor)
                        ?subject ?relation ?object .
                        FILTER(?relation = {self.relationships_filter[2]})

                        ?subject a ?subType .
                        FILTER(?subType IN ({self.observation_types[0]}))

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
        string_value = value.get("value")
        if value.get("type") == "uri":
            if "#" in string_value:
                return string_value.split("#")[-1]
            else:
                return string_value.split("/")[-1]

        return string_value

    def extract_entities_relationships(self) -> Dict[str, Any]:
        sparql = self.extract_entities_from_graphdb()
        self.raw_results = self._query_graphdb(sparql)
        self.devices = []
        self.assets = []
        self.observations = []
        self.relationships = []
        bindings = self.raw_results.get("results", {}).get("bindings", [])
        for row in bindings:
            subject = self._binding_value(row, "subject")
            type_name = self._binding_value(row, "type")
            relation = self._binding_value(row, "relation")
            obj = self._binding_value(row, "object")
            is_aggregated = self._binding_value(row, "isAggregatedSensor")
            has_id = self._binding_value(row, "hasId")

            if subject and type_name and relation is None and obj is None:
                if type_name.endswith("Device"):
                    self.devices.append({"subject": subject, "type": type_name})
                    if is_aggregated is not None:
                        self.devices[-1]["isAggregatedSensor"] = is_aggregated
                    if has_id is not None:
                        self.devices[-1]["hasId"] = has_id
                elif type_name.endswith("Observation"):
                    self.observations.append({"subject": subject, "type": type_name})
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
            "observations": self.observations,
            "relationships": self.relationships,
            "raw_results": self.raw_results,
        }