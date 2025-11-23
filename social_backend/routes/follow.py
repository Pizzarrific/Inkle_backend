# social_backend/routes/follow.py
from fastapi import APIRouter, HTTPException
import sqlite3
from crud import log_activity, create_notification, is_blocked_between

router = APIRouter(prefix="/follow", tags=["Follow"])
DB = "social.db"

@router.post("/add")
def follow_user(data: dict):
    follower = data.get("follower_id"); following = data.get("following_id")
    if not follower or not following:
        raise HTTPException(status_code=400, detail="Missing follower/following")
    if follower == following:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    if is_blocked_between(follower, following):
        raise HTTPException(status_code=403, detail="Action not allowed (blocked)")
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT id FROM followers WHERE follower_id=? AND following_id=?", (follower, following))
    if c.fetchone():
        conn.close(); raise HTTPException(status_code=400, detail="Already following")
    c.execute("INSERT INTO followers (follower_id, following_id) VALUES (?, ?)", (follower, following)); conn.commit(); conn.close()
    log_activity(follower, "followed_user", following)
    create_notification(user_id=following, type="follow", from_user=follower)
    return {"message": "Followed successfully"}
