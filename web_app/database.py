# web_app/database.py
"""
Very small wrapper around the SQLite DB used by the web app.
All tables are created on first run (init_db()).
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "users.db")

def _connect():
    """Open a connection (check_same_thread=False lets Streamlit rerun safely)."""
    return sqlite3.connect(DB_FILE, check_same_thread=False)

# ----------------------------------------------------------------------
# 1️⃣  Initialise the DB (tables only if they don't exist)
# ----------------------------------------------------------------------
def init_db() -> None:
    conn = _connect()
    cur = conn.cursor()
    # Users table
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        name TEXT,
        email TEXT,
        age INTEGER,
        gender TEXT,
        height REAL,
        weight REAL,
        activity_level TEXT,
        goal TEXT,
        diet_preferences TEXT,
        equipment TEXT,
        created_at TEXT
    )""")
    # Measurements table
    cur.execute("""CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        bmi REAL,
        body_fat REAL,
        weight REAL,
        measurements TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    # Workout plans table
    cur.execute("""CREATE TABLE IF NOT EXISTS workout_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plan_data TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    conn.commit()
    conn.close()

# ----------------------------------------------------------------------
# 2️⃣  USER CRUD
# ----------------------------------------------------------------------
def create_user(user: Dict[str, Any]) -> int:
    """Insert a user and return its generated id."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""INSERT INTO users
        (username,password_hash,name,email,age,gender,height,weight,activity_level,goal,
         diet_preferences,equipment,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
        (
            user.get("username", user["name"]),
            user.get("password_hash", ""),
            user["name"],
            user["email"],
            user["age"],
            user["gender"],
            user["height"],
            user["weight"],
            user["activity_level"],
            user["goal"],
            ",".join(user.get("diet_preferences", [])),
            ",".join(user.get("equipment", [])),
        )
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id

def get_latest_user() -> Dict[str, Any] | None:
    """Return the most recent user row (or None)."""
    conn = _connect()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)

def get_user_by_username(username: str) -> Dict[str, Any] | None:
    conn = _connect()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)

import bcrypt
def verify_user(username: str, password: str) -> Dict[str, Any] | None:
    user = get_user_by_username(username)
    if user and user.get("password_hash"):
        stored_hash = user["password_hash"]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return user
    return None
# ----------------------------------------------------------------------
# 3️⃣  MEASUREMENT CRUD
# ----------------------------------------------------------------------
def add_measurement(
    user_id: int,
    bmi: float,
    body_fat: float,
    weight: float,
    raw_measurements: str,
) -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""INSERT INTO measurements
        (user_id, date, bmi, body_fat, weight, measurements)
        VALUES (?,?,?,?,?,?)""",
        (user_id, datetime.now().isoformat(),
         bmi, body_fat, weight, raw_measurements))
    conn.commit()
    conn.close()

def get_measurements(user_id: int) -> List[Tuple]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM measurements
        WHERE user_id=? ORDER BY date DESC""", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ----------------------------------------------------------------------
# 4️⃣  WORKOUT PLAN CRUD
# ----------------------------------------------------------------------
def save_workout_plan(user_id: int, plan_dict: Dict) -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""INSERT INTO workout_plans
        (user_id, plan_data, created_at)
        VALUES (?,?,datetime('now'))""",
        (user_id, json.dumps(plan_dict)))
    conn.commit()
    conn.close()

def get_workout_plans(user_id: int) -> List[Tuple]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM workout_plans
        WHERE user_id=? ORDER BY created_at DESC""", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows
