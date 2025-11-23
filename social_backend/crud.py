# social_backend/crud.py
import sqlite3

DB = "social.db"

def log_activity(user_id, action, target_id=None):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO activity (user_id, action, target_id) VALUES (?, ?, ?)",
        (user_id, action, target_id)
    )
    conn.commit()
    conn.close()

def create_notification(user_id, type, from_user, post_id=None):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO notifications (user_id, type, from_user, post_id)
        VALUES (?, ?, ?, ?)
    """, (user_id, type, from_user, post_id))
    conn.commit()
    conn.close()

# Helpers for roles and blocking
def get_role(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id=?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else None

def is_blocked_between(a_id, b_id):
    """Return True if a blocked b or b blocked a"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT 1 FROM blocks WHERE blocker_id=? AND blocked_id=?", (a_id, b_id))
    if c.fetchone():
        conn.close()
        return True
    c.execute("SELECT 1 FROM blocks WHERE blocker_id=? AND blocked_id=?", (b_id, a_id))
    res = c.fetchone() is not None
    conn.close()
    return res
import sqlite3
DB = "social.db"

def get_user_role(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# crud.py (snippets)
import sqlite3

DB = "social.db"

def get_user_role(user_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def log_activity(user_id: int, action: str, target_id=None):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO activity (user_id, action, target_id) VALUES (?, ?, ?)",
              (user_id, action, target_id))
    conn.commit()
    conn.close()
