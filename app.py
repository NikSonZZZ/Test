from datetime import datetime, timezone
import sqlite3

from flask import Flask, jsonify, render_template_string, request


app = Flask(__name__)
DB_NAME = "readings.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farm_id INTEGER NOT NULL,
                device_id TEXT NOT NULL,
                sensor_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                received_at TEXT NOT NULL
            )
            """
        )


def validate_reading(data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object."

    required_fields = [
        "farmId",
        "deviceId",
        "sensorId",
        "sensorType",
        "value",
        "unit",
        "timestamp",
    ]

    for field in required_fields:
        if field not in data:
            return f"Missing field: {field}"

    try:
        float(data["value"])
    except (TypeError, ValueError):
        return "Field 'value' must be a number."

    return None


@app.route("/")
def dashboard():
    return render_template_string(
        """
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>FarmEdge Mini Prototype</title>
            <style>
                :root {
                    color-scheme: light;
                    --ink: #17212b;
                    --muted: #637083;
                    --line: #d7dee8;
                    --panel: #ffffff;
                    --bg: #f4f7f2;
                    --green: #2e7d4f;
                    --blue: #2563a8;
                    --amber: #b7791f;
                }

                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    background: var(--bg);
                    color: var(--ink);
                    font-family: Arial, Helvetica, sans-serif;
                }

                header {
                    border-bottom: 1px solid var(--line);
                    background: #ffffff;
                }

                .wrap {
                    width: min(1120px, calc(100% - 32px));
                    margin: 0 auto;
                }

                .topbar {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 16px;
                    padding: 18px 0;
                }

                h1 {
                    margin: 0;
                    font-size: 24px;
                    line-height: 1.2;
                }

                .status {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    color: var(--muted);
                    font-size: 14px;
                    white-space: nowrap;
                }

                .dot {
                    width: 10px;
                    height: 10px;
                    border-radius: 999px;
                    background: var(--green);
                    box-shadow: 0 0 0 4px rgba(46, 125, 79, 0.14);
                }

                main {
                    padding: 24px 0 40px;
                }

                .summary {
                    display: grid;
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                    gap: 12px;
                    margin-bottom: 18px;
                }

                .metric {
                    background: var(--panel);
                    border: 1px solid var(--line);
                    border-radius: 8px;
                    padding: 16px;
                }

                .metric span {
                    display: block;
                    color: var(--muted);
                    font-size: 13px;
                    margin-bottom: 8px;
                }

                .metric strong {
                    font-size: 26px;
                    line-height: 1;
                }

                .table-shell {
                    overflow: auto;
                    border: 1px solid var(--line);
                    border-radius: 8px;
                    background: var(--panel);
                }

                table {
                    width: 100%;
                    min-width: 860px;
                    border-collapse: collapse;
                }

                th,
                td {
                    padding: 12px 14px;
                    border-bottom: 1px solid var(--line);
                    text-align: left;
                    font-size: 14px;
                }

                th {
                    background: #eef3ed;
                    color: #344153;
                    font-size: 12px;
                    text-transform: uppercase;
                }

                tr:last-child td {
                    border-bottom: 0;
                }

                .reading-type {
                    color: var(--blue);
                    font-weight: 700;
                }

                .value {
                    color: var(--amber);
                    font-weight: 700;
                }

                .empty {
                    padding: 28px;
                    text-align: center;
                    color: var(--muted);
                    background: var(--panel);
                    border: 1px solid var(--line);
                    border-radius: 8px;
                }

                @media (max-width: 760px) {
                    .topbar,
                    .summary {
                        grid-template-columns: 1fr;
                        display: grid;
                    }

                    .status {
                        white-space: normal;
                    }
                }
            </style>
        </head>
        <body>
            <header>
                <div class="wrap topbar">
                    <h1>FarmEdge Mini Prototype Dashboard</h1>
                    <div class="status"><span class="dot"></span><span id="last-update">Waiting for readings</span></div>
                </div>
            </header>
            <main class="wrap">
                <section class="summary" aria-label="Reading summary">
                    <div class="metric"><span>Total readings</span><strong id="total-readings">0</strong></div>
                    <div class="metric"><span>Latest device</span><strong id="latest-device">-</strong></div>
                    <div class="metric"><span>Latest value</span><strong id="latest-value">-</strong></div>
                </section>

                <div id="empty-state" class="empty">No sensor readings yet. Start the fake sender or post a reading with Postman.</div>

                <section id="readings-table" class="table-shell" aria-label="Latest sensor readings" hidden>
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Farm</th>
                                <th>Device</th>
                                <th>Sensor</th>
                                <th>Type</th>
                                <th>Value</th>
                                <th>Recorded At</th>
                                <th>Received At</th>
                            </tr>
                        </thead>
                        <tbody id="readings"></tbody>
                    </table>
                </section>
            </main>

            <script>
                function formatReadingValue(reading) {
                    return `${reading.value} ${reading.unit}`;
                }

                async function loadReadings() {
                    const response = await fetch("/api/readings");
                    const readings = await response.json();
                    const tbody = document.getElementById("readings");
                    const emptyState = document.getElementById("empty-state");
                    const table = document.getElementById("readings-table");

                    tbody.innerHTML = "";
                    readings.forEach((reading) => {
                        const row = document.createElement("tr");
                        row.innerHTML = `
                            <td>${reading.id}</td>
                            <td>${reading.farm_id}</td>
                            <td>${reading.device_id}</td>
                            <td>${reading.sensor_id}</td>
                            <td class="reading-type">${reading.sensor_type}</td>
                            <td class="value">${formatReadingValue(reading)}</td>
                            <td>${reading.recorded_at}</td>
                            <td>${reading.received_at}</td>
                        `;
                        tbody.appendChild(row);
                    });

                    const latest = readings[0];
                    document.getElementById("total-readings").textContent = readings.length;
                    document.getElementById("latest-device").textContent = latest ? latest.device_id : "-";
                    document.getElementById("latest-value").textContent = latest ? formatReadingValue(latest) : "-";
                    document.getElementById("last-update").textContent = latest
                        ? `Updated ${new Date().toLocaleTimeString()}`
                        : "Waiting for readings";

                    emptyState.hidden = readings.length > 0;
                    table.hidden = readings.length === 0;
                }

                loadReadings();
                setInterval(loadReadings, 3000);
            </script>
        </body>
        </html>
        """
    )


@app.route("/api/readings", methods=["POST"])
def add_reading():
    data = request.get_json(silent=True)
    error = validate_reading(data)
    if error:
        return jsonify({"error": error}), 400

    received_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sensor_readings (
                farm_id, device_id, sensor_id, sensor_type, value, unit, recorded_at, received_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["farmId"],
                data["deviceId"],
                data["sensorId"],
                data["sensorType"],
                data["value"],
                data["unit"],
                data["timestamp"],
                received_at,
            ),
        )

    return jsonify({"message": "Reading saved successfully", "id": cursor.lastrowid}), 201


@app.route("/api/readings", methods=["GET"])
def get_readings():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM sensor_readings
            ORDER BY id DESC
            LIMIT 20
            """
        ).fetchall()

    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
