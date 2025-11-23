# models/posts.py

import sqlite3
from pydantic import BaseModel
from typing import Optional

DB = "social.db"


def init_posts_table():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Updated schema – store user_id not username
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT NOT NULL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# Pydantic model used in /posts/create
class Post(BaseModel):
    user_id: int
    content: str
    image_url: Optional[str] = None
