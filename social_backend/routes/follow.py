# routes/follow.py
from fastapi import APIRouter, HTTPException
import sqlite3
from crud import log_activity

router = APIRouter()
DB = "social.db"

@router.post("/add")
def follow_user(data: dict):
    follower = data.get("follower_id")
    following = data.get("following_id")
    if not follower or not following:
        raise HTTPException(400, "follower_id and following_id required")
    if follower == following:
        raise HTTPException(400, "Cannot follow yourself")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id FROM followers WHERE follower_id=? AND following_id=?", (follower, following))
    if c.fetchone():
        conn.close()
        raise HTTPException(400, "Already following")
    c.execute("INSERT INTO followers (follower_id, following_id) VALUES (?, ?)", (follower, following))
    conn.commit()
    conn.close()
    log_activity(follower, "followed_user", following)
    return {"message": "Followed successfully"}
