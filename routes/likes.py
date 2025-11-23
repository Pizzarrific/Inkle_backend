# routes/likes.py
from fastapi import APIRouter, HTTPException
import sqlite3
from crud import log_activity

router = APIRouter()
DB = "social.db"

@router.post("/add")
def add_like(data: dict):
    user_id = data.get("user_id")
    post_id = data.get("post_id")
    if not user_id or not post_id:
        raise HTTPException(400, "user_id and post_id required")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id FROM likes WHERE user_id=? AND post_id=?", (user_id, post_id))
    if c.fetchone():
        conn.close()
        raise HTTPException(400, "Already liked")
    c.execute("INSERT INTO likes (user_id, post_id) VALUES (?, ?)", (user_id, post_id))
    conn.commit()
    conn.close()
    log_activity(user_id, "liked_post", post_id)
    return {"message": "Post liked"}
