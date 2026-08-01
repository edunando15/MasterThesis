from dotenv import load_dotenv
from adapters.thingsboardAdapter import ThingsboardAdapter
import pandas as pd
import os
from generate_telemetry_values import generate_telemetry_values
import time

load_dotenv()
thingsboard_username = os.getenv("THINGSBOARD_USERNAME")
thingsboard_password = os.getenv("THINGSBOARD_PASSWORD")
tb_url = os.getenv("THINGSBOARD_URL")
sensors_file = '../data/thingsboard_registry.csv'
csv_file = pd.read_csv(sensors_file)
devices = csv_file[csv_file['type'] == 'DEVICE']

adapter = ThingsboardAdapter(platform_url=tb_url)
adapter.authenticate(user=thingsboard_username, password=thingsboard_password)

while True:
    for index, device in devices.iterrows():
        device_id = device['id']
        device_name = device['entity_uri']

        mock_values = generate_telemetry_values(device_name)

        telemetry = {
            "ts": int(pd.Timestamp.now().timestamp() * 1000),
            "values": mock_values
        }

        success = adapter.upload_telemetry(device_id, telemetry)
    time.sleep(10)
