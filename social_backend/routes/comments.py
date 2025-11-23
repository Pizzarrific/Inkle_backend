# social_backend/routes/comments.py
from fastapi import APIRouter, HTTPException, Query
import sqlite3
from crud import log_activity, create_notification, is_blocked_between

router = APIRouter(prefix="/comments", tags=["Comments"])
DB = "social.db"

@router.post("/add")
def add_comment(data: dict):
    user_id = data.get("user_id"); post_id = data.get("post_id"); text = data.get("text")
    if not user_id or not post_id or not text:
        raise HTTPException(status_code=400, detail="Missing data")
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT user_id FROM posts WHERE id=?", (post_id,)); row = c.fetchone()
    if not row:
        conn.close(); raise HTTPException(status_code=404, detail="Post not found")
    post_owner = row[0]
    if is_blocked_between(user_id, post_owner):
        conn.close(); raise HTTPException(status_code=403, detail="Action not allowed (blocked)")
    c.execute("INSERT INTO comments (user_id, post_id, text) VALUES (?, ?, ?)", (user_id, post_id, text)); conn.commit()
    conn.close()
    if post_owner != user_id:
        create_notification(user_id=post_owner, type="comment", from_user=user_id, post_id=post_id)
    log_activity(user_id, "commented_post", post_id)
    return {"message": "Comment added"}

@router.get("/post/{post_id}")
def get_comments(post_id: int, viewer_id: int = Query(None)):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT id, user_id, text, created_at FROM comments WHERE post_id=? ORDER BY created_at DESC", (post_id,))
    rows = c.fetchall(); conn.close()
    out = []
    for cid, uid, text, created_at in rows:
        if viewer_id and is_blocked_between(viewer_id, uid):
            continue
        out.append({"id": cid, "user_id": uid, "text": text, "created_at": created_at})
    return {"comments": out}
