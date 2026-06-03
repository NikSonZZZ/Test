import json
import os
import sys

import paho.mqtt.client as mqtt

from app import init_db, save_reading


MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "aug/#")


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
        print("Set them in PowerShell before running mqtt_listener.py.")
        sys.exit(1)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"Connected to HiveMQ Cloud. Subscribing to {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Could not connect to MQTT broker. Reason: {reason_code}")


def on_message(client, userdata, message):
    try:
        payload_text = message.payload.decode("utf-8")
        reading = json.loads(payload_text)
        reading_id = save_reading(reading)
        print(f"Saved MQTT reading #{reading_id} from topic {message.topic}")
    except Exception as exc:
        print(f"Skipped MQTT message from {message.topic}: {exc}")


def main():
    require_config()
    init_db()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="team171-backend-listener")
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Connecting to {MQTT_HOST}:{MQTT_PORT}")
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
