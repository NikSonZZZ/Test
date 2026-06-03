from datetime import datetime, timedelta, timezone
import json
import os
import random
import sys
import time

import paho.mqtt.client as mqtt


MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_PUBLISH_TOPIC", "aug/brisbane-01/fish/zone-a/esp32-01/telemetry")
BRISBANE_TZ = timezone(timedelta(hours=10))

SENSORS = [
    {"sensorId": "temp-001", "sensorType": "temperature", "unit": "C", "minimum": 20.0, "maximum": 32.0},
    {"sensorId": "soil-001", "sensorType": "soil_moisture", "unit": "%", "minimum": 35.0, "maximum": 82.0},
    {"sensorId": "ph-001", "sensorType": "ph", "unit": "pH", "minimum": 5.8, "maximum": 7.4},
]


def require_config():
    missing = [
        name
        for name, value in {
            "MQTT_HOST": MQTT_HOST,
            "MQTT_USERNAME": MQTT_USERNAME,
            "MQTT_PASSWORD": MQTT_PASSWORD,
        }.items()
        if not value
    ]
    if missing:
        print(f"Missing MQTT settings: {', '.join(missing)}")
        print("Set them in PowerShell before running mqtt_sender.py.")
        sys.exit(1)


def build_message():
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
    require_config()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="team171-test-publisher")
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()

    print(f"Publishing fake MQTT readings to {MQTT_TOPIC}. Press Ctrl+C to stop.")
    try:
        while True:
            message = build_message()
            client.publish(MQTT_TOPIC, json.dumps(message), qos=1)
            print(f"Published {message['sensorType']}={message['value']} {message['unit']}")
            time.sleep(3)
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
