# FarmEdge Mini Prototype

This project is a small prototype that simulates sensor readings being sent from a Raspberry Pi to a backend dashboard.

The prototype has:

- a Flask backend API
- a local SQLite database
- a dashboard page
- a fake sensor sender script

## Files

- `app.py` - runs the backend API, creates the database, and shows the dashboard
- `sender.py` - simulates a Raspberry Pi by sending fake sensor readings
- `requirements.txt` - lists the Python packages needed for the project

## Open The Project Folder

Open the extracted project folder in Terminal or PowerShell.

On Windows, you can usually right-click inside the folder and choose **Open in Terminal**.

## Create A Virtual Environment

Run:

```powershell
python -m venv .venv
```

If `python` does not work, run:

```powershell
py -m venv .venv
```

This creates a `.venv` folder inside the project. It keeps this project's Python packages separate from the computer's main Python setup.

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

This installs Flask and Requests inside the `.venv` environment.

## Start The Dashboard

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