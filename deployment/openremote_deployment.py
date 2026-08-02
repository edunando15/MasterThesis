from dotenv import load_dotenv
import os
import pandas as pd
from extractors.openRemoteExtractor import OpenRemoteExtractor
from adapters.openRemoteAdapter import OpenRemoteAdapter
from .openRemoteDeployer import OpenRemoteDeployer

def execute_openremote_deployment():
    load_dotenv()
    graphdb_url = os.getenv("GRAPHDB_URL")
    graphdb_repository = os.getenv("GRAPHDB_REPOSITORY")
    or_username = os.getenv("OPENREMOTE_USERNAME")
    or_password = os.getenv("OPENREMOTE_PASSWORD")
    or_url = os.getenv("OPENREMOTE_URL")
    or_realm = os.getenv("OPENREMOTE_REALM")

    openremote_extractor = OpenRemoteExtractor(graphdb_url, graphdb_repository)
    or_extracted_entities = openremote_extractor.extract_entities_relationships()

    or_adapter = OpenRemoteAdapter(or_url)
    or_adapter.set_realm(or_realm)
    or_deployer = OpenRemoteDeployer(or_adapter, or_extracted_entities)
    or_registry = or_deployer.deploy(or_username, or_password)
    or_registry_data = [
        {
            "entity_uri": uri,
            "id": data["id"],
            "type": data["type"].value,
            "observations": data.get("observations", []),
        }
        for uri, data in or_registry.items()
    ]
    registry_df = pd.DataFrame(or_registry_data)
    registry_df.to_csv("data/openremote_registry.csv", index=False)