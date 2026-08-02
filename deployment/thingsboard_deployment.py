from dotenv import load_dotenv
import os
import pandas as pd
from extractors.thingsboardExtractor import ThingsboardExtractor
from adapters.thingsboardAdapter import ThingsboardAdapter
from .thingsboardDeployer import ThingsboardDeployer

def execute_thingsboard_deployment():
    load_dotenv()
    graphdb_url = os.getenv("GRAPHDB_URL")
    graphdb_repository = os.getenv("GRAPHDB_REPOSITORY")
    thingsboard_username = os.getenv("THINGSBOARD_USERNAME")
    thingsboard_password = os.getenv("THINGSBOARD_PASSWORD")
    tb_url = os.getenv("THINGSBOARD_URL")
    thingsboard_extractor = ThingsboardExtractor(graphdb_url, graphdb_repository)
    extracted_entities = thingsboard_extractor.extract_entities_relationships()

    adapter = ThingsboardAdapter(tb_url)
    deployer = ThingsboardDeployer(adapter, extracted_entities)

    registry = deployer.deploy(thingsboard_username, thingsboard_password)

    registry_data = [
        {"entity_uri": uri, "id": data["id"], "type": data["type"].value}
        for uri, data in registry.items()
    ]
    registry_df = pd.DataFrame(registry_data)
    registry_df.to_csv("data/thingsboard_registry.csv", index=False)