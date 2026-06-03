# FarmEdge Mini Prototype

This project is a small prototype that simulates sensor readings being sent from a Raspberry Pi to a backend dashboard.

The prototype has:

- a Flask backend API
- a local SQLite database
- a dashboard page
- a fake sensor sender script
- an MQTT listener for HiveMQ Cloud
- an MQTT test sender

## Files

- `app.py` - runs the backend API, creates the database, and shows the dashboard
- `sender.py` - simulates a Raspberry Pi by sending fake sensor readings
- `mqtt_listener.py` - receives MQTT messages from HiveMQ Cloud and saves them to the database
- `mqtt_sender.py` - sends fake MQTT readings to HiveMQ Cloud for testing
- `requirements.txt` - lists the Python packages needed for the project

## Open The Project Folder

Open the extracted project folder in Terminal or PowerShell.

On Windows, you can usually right-click inside the folder and choose **Open in Terminal**.

## Create A Virtual Environment

Run:

```powershell
python -m venv .venv
```

## Activate The Virtual Environment

Run:

```powershell
.\.venv\Scripts\activate
```

After this, your terminal may show `(.venv)` at the start of the line. That means the virtual environment is active.

## Install Requirements

Run:

```powershell
pip install -r requirements.txt
```

This installs Flask, Requests, and Paho MQTT inside the `.venv` environment.

## Start The Dashboard (REST API Setup)

Run:

```powershell
python app.py
```

Then open this link in your browser:

```text
http://127.0.0.1:5000
```

The dashboard should load, but it may not show many readings yet.

## Start The Fake Sensor Sender

Open a second Terminal or PowerShell window in the same project folder.

Activate the virtual environment again:

```powershell
.\.venv\Scripts\activate
```

Then run:

```powershell
python sender.py
```

Leave this second window open. It sends a new fake sensor reading every 3 seconds.

## Start The Dashboard (HiveMQ Cloud Setup)

HiveMQ Cloud is the central MQTT broker. It sits between the Raspberry Pi and the backend.

The flow is:

```text
Raspberry Pi / MQTT test sender
  -> HiveMQ Cloud broker
  -> mqtt_listener.py
  -> SQLite database
  -> dashboard
```

### 1. Start The Dashboard

In the first terminal:

```powershell
.\.venv\Scripts\activate
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

### 2. Start The MQTT Listener

In the second terminal:

```powershell
.\.venv\Scripts\activate
```

Set the MQTT environment variables, then run:

```powershell
$env:MQTT_HOST="your-cluster-url.s1.eu.hivemq.cloud"
$env:MQTT_PORT="8883"
$env:MQTT_USERNAME="your-mqtt-username"
$env:MQTT_PASSWORD="your-mqtt-password"
python mqtt_listener.py
```

Leave this running. It waits for MQTT messages and saves them into the database.

### 3. Test With The MQTT Sender

In the third terminal:

```powershell
.\.venv\Scripts\activate
```

Set the same MQTT environment variables, then run:

```powershell
$env:MQTT_HOST="your-cluster-url.s1.eu.hivemq.cloud"
$env:MQTT_PORT="8883"
$env:MQTT_USERNAME="your-mqtt-username"
$env:MQTT_PASSWORD="your-mqtt-password"
python mqtt_sender.py
```

This publishes a fake MQTT reading every 3 seconds.

The dashboard should start showing those readings.

## MQTT Message Format

The MQTT sender and listener use this JSON structure:

```json
{
  "farmId": 1,
  "deviceId": "pi-001",
  "sensorId": "temp-001",
  "sensorType": "temperature",
  "value": 24.7,
  "unit": "C",
  "timestamp": "2026-06-02T12:30:00+10:00"
}
```

If you want to send a different JSON structure, database and send/receive methods have to be updated.

## What Should Happen

The dashboard automatically refreshes every 3 seconds.

When `sender.py` is running, the dashboard should show new readings such as:

- temperature
- soil moisture
- humidity

## Stop The Project

To stop the dashboard or sender, press:

```text
Ctrl + C
```

in each terminal window.
