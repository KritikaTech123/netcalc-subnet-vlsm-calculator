import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from calculations import subnet_calculation, vlsm_calculation

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "netcalc.db"
DB_PATH.parent.mkdir(exist_ok=True)
app = Flask(__name__)
CORS(app)


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, calculation_type TEXT NOT NULL,
            input_details TEXT NOT NULL, output_details TEXT NOT NULL,
            created_at TEXT NOT NULL)""")


def save_history(kind, inputs, output):
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO calculations (calculation_type,input_details,output_details,created_at) VALUES (?,?,?,?)",
            (kind, json.dumps(inputs), json.dumps(output), datetime.now(timezone.utc).isoformat()),
        )
        return cursor.lastrowid


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/calculate/subnet")
def calculate_subnet():
    data = request.get_json(silent=True) or {}
    try:
        result = subnet_calculation(data.get("address", ""), int(data.get("prefix", -1)), data.get("mask") or None)
        save_history("subnet", data, result)
        return jsonify(result)
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/calculate/vlsm")
def calculate_vlsm():
    data = request.get_json(silent=True) or {}
    try:
        result = vlsm_calculation(data.get("network", ""), data.get("departments", []))
        save_history("vlsm", data, result)
        return jsonify(result)
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/history")
def history():
    with get_db() as db:
        rows = db.execute("SELECT * FROM calculations ORDER BY id DESC").fetchall()
    return jsonify([{
        "id": row["id"], "type": row["calculation_type"],
        "inputs": json.loads(row["input_details"]), "output": json.loads(row["output_details"]),
        "created_at": row["created_at"],
    } for row in rows])


@app.delete("/api/history/<int:record_id>")
def delete_history(record_id):
    with get_db() as db:
        cursor = db.execute("DELETE FROM calculations WHERE id = ?", (record_id,))
    if cursor.rowcount == 0:
        return jsonify({"error": "History record not found."}), 404
    return jsonify({"message": "History record deleted."})


@app.delete("/api/history")
def clear_history():
    with get_db() as db:
        db.execute("DELETE FROM calculations")
    return jsonify({"message": "History cleared."})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
