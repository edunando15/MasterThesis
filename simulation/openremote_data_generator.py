from dotenv import load_dotenv
from adapters.openRemoteAdapter import OpenRemoteAdapter
import pandas as pd
import ast
import os
from generate_telemetry_values import generate_telemetry_values_with_observations
import time

load_dotenv()

or_username = os.getenv("OPENREMOTE_USERNAME")
or_password = os.getenv("OPENREMOTE_PASSWORD")
or_url = os.getenv("OPENREMOTE_URL")
or_realm = os.getenv("OPENREMOTE_REALM")

sensors_file = '../data/openremote_registry.csv'
csv_file = pd.read_csv(sensors_file)
devices = csv_file[csv_file['type'] == 'DEVICE']

adapter = OpenRemoteAdapter(platform_url=or_url)
adapter.set_realm(or_realm)
adapter.authenticate(user=or_username, password=or_password)

while True:
    for index, device in devices.iterrows():
        device_id = device['id']
        device_name = device['entity_uri']
        device_observations = device['observations']
        if pd.isna(device_observations):
            device_observations = []
        else:
            device_observations = ast.literal_eval(device_observations)
        mock_values = generate_telemetry_values_with_observations(device_name, device_observations)
        success = adapter.upload_telemetry(device_id, mock_values)
        if success:
            print(f"Data uploaded for {device_name}")
        else:
            print(f"Data not uploaded for {device_name}")
    time.sleep(10)
