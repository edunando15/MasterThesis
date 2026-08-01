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
        values["status"] = "active"

    return values

def generate_telemetry_values_with_observations(device_name: str, device_observations: list) -> dict:
    values = {}
    if not device_observations:
        return values
    for obs in device_observations:
        obs_lower = obs.lower()
        if "temperature" in obs_lower:
            if "target" in obs_lower:
                values[obs] = round(random.uniform(20.0, 24.0), 1)
            else:
                values[obs] = round(random.uniform(18.0, 25.0), 2)

        elif "humidity" in obs_lower:
            values[obs] = round(random.uniform(35.0, 60.0), 2)

        elif "co2" in obs_lower:
            values[obs] = random.randint(400, 800)

        elif "co" in obs_lower and "co2" not in obs_lower:
            values[obs] = round(random.uniform(0.0, 5.0), 2)

        elif "pm25" in obs_lower:
            values[obs] = round(random.uniform(0.0, 25.0), 2)

        elif "pm10" in obs_lower:
            values[obs] = round(random.uniform(0.0, 50.0), 2)

        elif "valve" in obs_lower or "radiator" in obs_lower:
            values[obs] = random.randint(0, 100)

        else:
            values[obs] = "active"

    return values