# social_backend/routes/posts.py
from fastapi import APIRouter, HTTPException, Query
import sqlite3
from crud import log_activity, is_blocked_between

router = APIRouter(prefix="/posts", tags=["Posts"])
DB = "social.db"

@router.post("/create")
def create_post(data: dict):
    user_id = data.get("user_id"); content = data.get("content")
    if not user_id or content is None:
        raise HTTPException(status_code=400, detail="Missing user_id/content")
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)", (user_id, content))
    pid = c.lastrowid; conn.commit(); conn.close()
    log_activity(user_id, "created_post", pid)
    return {"message": "Post created", "post_id": pid}

@router.get("/all")
def all_posts(viewer_id: int = Query(None), limit: int = Query(50), offset: int = Query(0)):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("""
        SELECT posts.id, posts.user_id, users.username, posts.content, posts.timestamp
        FROM posts LEFT JOIN users ON users.id = posts.user_id
        ORDER BY posts.timestamp DESC LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = c.fetchall(); conn.close()
    out = []
    for pid, uid, username, content, ts in rows:
        if viewer_id and is_blocked_between(viewer_id, uid):
            continue
        out.append({"post_id": pid, "user_id": uid, "username": username, "content": content, "timestamp": ts})
    return out
