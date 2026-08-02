import os
import requests
from dotenv import load_dotenv

load_dotenv()

def upload_to_graphdb(file_bytes):
    graphdb_url = os.getenv("GRAPHDB_URL")
    repo = os.getenv("GRAPHDB_REPOSITORY")

    if not graphdb_url or not repo:
        raise ValueError("GraphDB configuration missing in environment variables.")

    endpoint = f"{graphdb_url}/repositories/{repo}/statements"
    headers = {"Content-Type": "application/x-turtle"}

    response = requests.post(endpoint, headers=headers, data=file_bytes)
    response.raise_for_status()
    print("Successfully uploaded to GraphDB.")