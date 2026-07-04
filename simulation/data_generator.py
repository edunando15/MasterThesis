from dotenv import load_dotenv
from adapters.thingsboardAdapter import ThingsboardAdapter
import pandas as pd
import os
import random


def generate_telemetry_values(device_name: str) -> dict:
    name_lower = device_name.lower()
    values = {}

    if "multisensor" in name_lower:
        values["temperature"] = round(random.uniform(18.0, 25.0), 2)
        values["humidity"] = round(random.uniform(35.0, 60.0), 2)
        values["co2"] = random.randint(400, 800)

    elif "temperature" in name_lower:
        values["temperature"] = round(random.uniform(18.0, 25.0), 2)

    elif "relativehumidity" in name_lower:
        values["humidity"] = round(random.uniform(35.0, 60.0), 2)

    elif "co2" in name_lower:
        values["co2"] = random.randint(400, 800)

    elif "cosensor" in name_lower:
        values["co"] = round(random.uniform(0.0, 5.0), 2)

    elif "pm25" in name_lower:
        values["pm25"] = round(random.uniform(0.0, 25.0), 2)

    elif "pm10" in name_lower:
        values["pm10"] = round(random.uniform(0.0, 50.0), 2)

    elif "radiator" in name_lower:
        values["valve_state"] = random.randint(0, 100)
        values["target_temperature"] = round(random.uniform(20.0, 24.0), 1)

    else:
        # Fallback for unrecognized device types
        values["status"] = "active"

    return values


load_dotenv()
thingsboard_username = os.getenv("THINGSBOARD_USERNAME")
thingsboard_password = os.getenv("THINGSBOARD_PASSWORD")
tb_url = os.getenv("THINGSBOARD_URL")
sensors_file = '../data/registry.csv'
csv_file = pd.read_csv(sensors_file)
devices = csv_file[csv_file['type'] == 'DEVICE']

adapter = ThingsboardAdapter(platform_url=tb_url)
adapter.authenticate(user=thingsboard_username, password=thingsboard_password)

for index, device in devices.iterrows():
    device_id = device['id']
    device_name = device['entity_uri']

    mock_values = generate_telemetry_values(device_name)

    telemetry = {
        "ts": int(pd.Timestamp.now().timestamp() * 1000),
        "values": mock_values
    }

    success = adapter.upload_telemetry(device_id, telemetry)
