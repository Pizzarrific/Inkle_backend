# models/followers.py
import sqlite3
DB = "social.db"

def init_followers_table():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS followers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            follower_id INTEGER,
            following_id INTEGER
        )
    """)
    conn.commit()
    conn.close()
