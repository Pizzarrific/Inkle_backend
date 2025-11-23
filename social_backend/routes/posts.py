# routes/posts.py
from fastapi import APIRouter, HTTPException
import sqlite3
from crud import log_activity

router = APIRouter()
DB = "social.db"

@router.post("/create")
def create_post(data: dict):
    user_id = data.get("user_id")
    content = data.get("content", "")
    if not user_id or not content:
        raise HTTPException(400, "user_id and content required")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)", (user_id, content))
    conn.commit()
    post_id = c.lastrowid
    conn.close()
    log_activity(user_id, "created_post", post_id)
    return {"message": "Post created", "post_id": post_id}

@router.get("/all")
def get_all_posts():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, user_id, content, image_url, created_at FROM posts ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    posts = [{"id": r[0], "user_id": r[1], "content": r[2], "image_url": r[3], "created_at": r[4]} for r in rows]
    return {"posts": posts}
