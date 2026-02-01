import sqlite3
import json
from datetime import datetime
import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OLD_DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "primemodel.db"))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "primemodel.db"))

logging.basicConfig(level=logging.INFO)

def _ensure_db_path():
    data_dir = os.path.dirname(DB_PATH)
    try:
        os.makedirs(data_dir, exist_ok=True)
    except Exception as exc:
        logging.exception("Failed to create data directory: %s", exc)

    try:
        if os.path.exists(OLD_DB_PATH) and not os.path.exists(DB_PATH):
            os.replace(OLD_DB_PATH, DB_PATH)
    except Exception as exc:
        logging.exception("Failed to move database file: %s", exc)

def _init_db():
    try:
        _ensure_db_path()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id TEXT,
                asset_type TEXT,
                prediction_type TEXT,
                result_json TEXT,
                created_at TEXT
            )
            """
        )
        conn.commit()
    except Exception as exc:
        logging.exception("Failed to initialize database: %s", exc)
    finally:
        try:
            conn.close()
        except Exception:
            pass

_init_db()

def save_prediction(asset_id, asset_type, prediction_type, result_dict):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO predictions (asset_id, asset_type, prediction_type, result_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                asset_id,
                asset_type,
                prediction_type,
                json.dumps(result_dict),
                datetime.utcnow().isoformat() + "Z",
            ),
        )
        conn.commit()
    except Exception as exc:
        logging.exception("Failed to save prediction: %s", exc)
    finally:
        try:
            conn.close()
        except Exception:
            pass
