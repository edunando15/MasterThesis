import os
from adapters.thingsboardAdapter import ThingsboardAdapter as ThingsboardAdapter
from extractors.entityExtractor import EntityExtractor
from deployment.thingsboardDeployer import ThingsboardDeployer
from dotenv import load_dotenv

load_dotenv()
graphdb_url = os.getenv("GRAPHDB_URL")
graphdb_repository = os.getenv("GRAPHDB_REPOSITORY")
thingsboard_username = os.getenv("THINGSBOARD_USERNAME")
thingsboard_password = os.getenv("THINGSBOARD_PASSWORD")
tb_url = os.getenv("THINGSBOARD_URL")

extractor = EntityExtractor(graphdb_url, graphdb_repository)
extracted_entities = extractor.extract_entities_relationships()

adapter = ThingsboardAdapter(tb_url)
deployer = ThingsboardDeployer(adapter, extracted_entities)

deployer.deploy(thingsboard_username, thingsboard_password)
