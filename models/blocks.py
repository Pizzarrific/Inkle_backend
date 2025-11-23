# models/blocks.py
import sqlite3
DB = "social.db"

def init_blocks_table():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blocker_id INTEGER,
            blocked_id INTEGER
        )
    """)
    conn.commit()
    conn.close()
