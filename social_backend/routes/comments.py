# routes/comments.py
from fastapi import APIRouter, HTTPException
import sqlite3
from crud import log_activity

router = APIRouter()
DB = "social.db"

@router.post("/add")
def add_comment(data: dict):
    user_id = data.get("user_id")
    post_id = data.get("post_id")
    text = data.get("text", "").strip()
    if not user_id or not post_id or not text:
        raise HTTPException(400, "user_id, post_id and text required")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO comments (user_id, post_id, text) VALUES (?, ?, ?)", (user_id, post_id, text))
    conn.commit()
    conn.close()
    log_activity(user_id, "commented_post", post_id)
    return {"message": "Comment added"}

@router.get("/post/{post_id}")
def get_comments(post_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, user_id, text, created_at FROM comments WHERE post_id=? ORDER BY created_at DESC", (post_id,))
    rows = c.fetchall()
    conn.close()
    comments = [{"id": r[0], "user_id": r[1], "text": r[2], "created_at": r[3]} for r in rows]
    return {"comments": comments}
