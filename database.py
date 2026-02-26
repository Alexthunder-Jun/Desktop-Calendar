import sqlite3
import os
from datetime import date, datetime


def _db_path():
    app_dir = os.path.join(os.path.expanduser("~"), ".daily_event")
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, "todos.db")


def get_connection():
    conn = sqlite3.connect(_db_path(), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            deadline DATE NOT NULL,
            alarm_time DATETIME,
            alarm_notified INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_todo(title: str, deadline: date, alarm_time: datetime = None) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO todos (title, deadline, alarm_time) VALUES (?, ?, ?)",
        (title, deadline, alarm_time),
    )
    todo_id = cur.lastrowid
    conn.commit()
    conn.close()
    return todo_id


def get_todos_by_date(target_date: date) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM todos WHERE deadline = ? ORDER BY completed, created_at",
        (target_date,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_todos() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM todos ORDER BY deadline, completed, created_at"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def toggle_completed(todo_id: int):
    conn = get_connection()
    conn.execute(
        "UPDATE todos SET completed = CASE WHEN completed = 0 THEN 1 ELSE 0 END WHERE id = ?",
        (todo_id,),
    )
    conn.commit()
    conn.close()


def update_alarm(todo_id: int, alarm_time: datetime):
    conn = get_connection()
    conn.execute(
        "UPDATE todos SET alarm_time = ?, alarm_notified = 0 WHERE id = ?",
        (alarm_time, todo_id),
    )
    conn.commit()
    conn.close()


def update_deadline(todo_id: int, new_deadline: date):
    conn = get_connection()
    conn.execute(
        "UPDATE todos SET deadline = ? WHERE id = ?",
        (new_deadline, todo_id),
    )
    conn.commit()
    conn.close()


def delete_todo(todo_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()


def get_pending_alarms() -> list:
    now = datetime.now()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM todos WHERE alarm_time IS NOT NULL AND alarm_notified = 0 AND alarm_time <= ? AND completed = 0",
        (now,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_alarm_notified(todo_id: int):
    conn = get_connection()
    conn.execute("UPDATE todos SET alarm_notified = 1 WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()


def get_dates_with_todos() -> set:
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT deadline FROM todos WHERE completed = 0"
    ).fetchall()
    conn.close()
    return {row["deadline"] for row in rows if row["deadline"]}
