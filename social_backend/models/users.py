# models/users.py

import sqlite3

DB = "social.db"

def init_users_table():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Create users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)
    conn.commit()

    # Ensure column "role" exists
    c.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in c.fetchall()]

    if "role" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        conn.commit()

    conn.close()
