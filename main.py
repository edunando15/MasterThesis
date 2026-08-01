import os
from adapters.thingsboardAdapter import ThingsboardAdapter as ThingsboardAdapter
from adapters.openRemoteAdapter import OpenRemoteAdapter as OpenRemoteAdapter
from extractors.thingsboardExtractor import ThingsboardExtractor
from extractors.openRemoteExtractor import OpenRemoteExtractor
from deployment.thingsboardDeployer import ThingsboardDeployer
from deployment.openRemoteDeployer import OpenRemoteDeployer
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
graphdb_url = os.getenv("GRAPHDB_URL")
graphdb_repository = os.getenv("GRAPHDB_REPOSITORY")
thingsboard_username = os.getenv("THINGSBOARD_USERNAME")
thingsboard_password = os.getenv("THINGSBOARD_PASSWORD")
tb_url = os.getenv("THINGSBOARD_URL")
or_username = os.getenv("OPENREMOTE_USERNAME")
or_password = os.getenv("OPENREMOTE_PASSWORD")
or_url = os.getenv("OPENREMOTE_URL")
or_realm = os.getenv("OPENREMOTE_REALM")

# Thingsboard deployment
"""

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

"""

# OpenRemote deployment
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