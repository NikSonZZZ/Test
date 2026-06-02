from datetime import datetime, timedelta, timezone
import random
import time

import requests


API_URL = "http://127.0.0.1:5000/api/readings"
BRISBANE_TZ = timezone(timedelta(hours=10))

SENSORS = [
    {"sensorId": "temp-001", "sensorType": "temperature", "unit": "C", "minimum": 20.0, "maximum": 32.0},
    {"sensorId": "soil-001", "sensorType": "soil_moisture", "unit": "%", "minimum": 35.0, "maximum": 82.0},
    {"sensorId": "humid-001", "sensorType": "humidity", "unit": "%", "minimum": 45.0, "maximum": 90.0},
]


def build_reading():
    sensor = random.choice(SENSORS)
    return {
        "farmId": 1,
        "deviceId": "pi-001",
        "sensorId": sensor["sensorId"],
        "sensorType": sensor["sensorType"],
        "value": round(random.uniform(sensor["minimum"], sensor["maximum"]), 2),
        "unit": sensor["unit"],
        "timestamp": datetime.now(BRISBANE_TZ).isoformat(),
    }


def main():
    print("Sending fake FarmEdge sensor readings. Press Ctrl+C to stop.")
    while True:
        reading = build_reading()
        try:
            response = requests.post(API_URL, json=reading, timeout=10)
            print(f"Sent {reading['sensorType']}={reading['value']} {reading['unit']} -> {response.status_code}")
        except requests.RequestException as exc:
            print(f"Could not send reading: {exc}")
        time.sleep(3)


if __name__ == "__main__":
    main()
