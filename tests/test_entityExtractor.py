import unittest
from unittest.mock import patch
import os
from extractors.entityExtractor import EntityExtractor
from dotenv import load_dotenv

load_dotenv()
graphdb_url = os.getenv("GRAPHDB_URL")
graphdb_repository = os.getenv("GRAPHDB_REPOSITORY")

class EntityExtractorTest(unittest.TestCase):

    def test_extract_returns_expected_structure(self):
        extractor = EntityExtractor(graphdb_url, graphdb_repository)
        fake_response = {
            "results": {
                "bindings": [
                    {
                        "subject": {"value": "urn:device1"},
                        "type": {"value": "iotpo:Device"},
                        "relation": {},
                        "object": {},
                    },
                    {
                        "subject": {"value": "urn:site1"},
                        "type": {"value": "bot:Building"},
                        "relation": {},
                        "object": {},
                    },
                    {
                        "subject": {"value": "urn:zone1"},
                        "type": {"value": "bot:Zone"},
                        "relation": {"value": "bot:hasBuilding"},
                        "object": {"value": "urn:building1"},
                    },
                ]
            }
        }

        with patch.object(extractor, "_query_graphdb", return_value=fake_response):
            result = extractor.extract_entities_relationships()

        assert set(result.keys()) == {"assets", "devices", "relationships", "raw_results"}

        assert result["assets"] == [{"subject": "urn:site1", "type": "bot:Building"}]
        assert result["devices"] == [{"subject": "urn:device1", "type": "iotpo:Device"}]

        assert result["relationships"] == [
            {
                "subject": "urn:zone1",
                "relation": "bot:hasBuilding",
                "object": "urn:building1",
            }
        ]

        assert result["raw_results"] == fake_response
