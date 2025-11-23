# social_backend/routes/likes.py
from fastapi import APIRouter, HTTPException
import sqlite3
from crud import log_activity, create_notification, is_blocked_between

router = APIRouter(prefix="/likes", tags=["Likes"])
DB = "social.db"

@router.post("/add")
def like_post(data: dict):
    user_id = data.get("user_id"); post_id = data.get("post_id")
    if not user_id or not post_id:
        raise HTTPException(status_code=400, detail="Missing user_id/post_id")
    conn = sqlite3.connect(DB); c = conn.cursor()
    # check post owner
    c.execute("SELECT user_id FROM posts WHERE id=?", (post_id,)); row = c.fetchone()
    if not row:
        conn.close(); raise HTTPException(status_code=404, detail="Post not found")
    post_owner = row[0]
    # prevent likes if blocked relation
    if is_blocked_between(user_id, post_owner):
        conn.close(); raise HTTPException(status_code=403, detail="Action not allowed (blocked)")
    c.execute("SELECT id FROM likes WHERE user_id=? AND post_id=?", (user_id, post_id)); ifexists = c.fetchone()
    if ifexists:
        conn.close(); raise HTTPException(status_code=400, detail="Already liked")
    c.execute("INSERT INTO likes (user_id, post_id) VALUES (?, ?)", (user_id, post_id)); conn.commit()
    conn.close()
    # notify + activity
    if post_owner != user_id:
        create_notification(user_id=post_owner, type="like", from_user=user_id, post_id=post_id)
    log_activity(user_id, "liked_post", post_id)
    return {"message": "Post liked"}
