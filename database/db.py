import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'mindsprout.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            device_id   TEXT PRIMARY KEY,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_visit  DATE,
            streak      INTEGER DEFAULT 0,
            max_streak  INTEGER DEFAULT 0,
            total_sessions INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id        TEXT,
            session_date     DATE,
            mood             TEXT,
            stages_completed INTEGER DEFAULT 0,
            completed        BOOLEAN DEFAULT 0,
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES users(device_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id   TEXT,
            badge_name  TEXT,
            badge_icon  TEXT,
            earned_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(device_id, badge_name),
            FOREIGN KEY (device_id) REFERENCES users(device_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


def get_or_create_user(device_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE device_id = ?", (device_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute(
            "INSERT INTO users (device_id, last_visit) VALUES (?, DATE('now'))",
            (device_id,)
        )
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE device_id = ?", (device_id,))
        user = cursor.fetchone()
    conn.close()
    return dict(user)


def get_today_session(device_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM sessions WHERE device_id = ? AND session_date = DATE('now')",
        (device_id,)
    )
    session = cursor.fetchone()
    conn.close()
    return dict(session) if session else None


def create_session(device_id, mood):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (device_id, session_date, mood) VALUES (?, DATE('now'), ?)",
        (device_id, mood)
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def update_session_progress(device_id, stages_completed, completed=False):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE sessions SET stages_completed = ?, completed = ?
           WHERE device_id = ? AND session_date = DATE('now')''',
        (stages_completed, 1 if completed else 0, device_id)
    )
    conn.commit()
    conn.close()


def update_streak(device_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT last_visit, streak, max_streak FROM users WHERE device_id = ?", (device_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return 0

    last_visit = user['last_visit']
    streak = user['streak']
    max_streak = user['max_streak']

    cursor.execute("SELECT DATE('now') as today, DATE('now', '-1 day') as yesterday")
    dates = cursor.fetchone()
    today = dates['today']
    yesterday = dates['yesterday']

    if last_visit == today:
        conn.close()
        return streak
    elif last_visit == yesterday:
        streak += 1
    else:
        streak = 1

    max_streak = max(max_streak, streak)

    cursor.execute(
        '''UPDATE users SET streak = ?, max_streak = ?,
           last_visit = DATE('now'), total_sessions = total_sessions + 1
           WHERE device_id = ?''',
        (streak, max_streak, device_id)
    )
    conn.commit()
    conn.close()
    return streak


def award_badge(device_id, badge_name, badge_icon):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO badges (device_id, badge_name, badge_icon) VALUES (?, ?, ?)",
            (device_id, badge_name, badge_icon)
        )
        conn.commit()
        awarded = cursor.rowcount > 0
    except Exception:
        awarded = False
    conn.close()
    return awarded


def get_user_badges(device_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT badge_name, badge_icon, earned_at FROM badges WHERE device_id = ? ORDER BY earned_at",
        (device_id,)
    )
    badges = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return badges