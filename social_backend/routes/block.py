# routes/block.py
from fastapi import APIRouter, HTTPException
import sqlite3
from crud import log_activity

router = APIRouter()
DB = "social.db"

@router.post("/add")
def add_block(data: dict):
    blocker = data.get("blocker_id")
    blocked = data.get("blocked_id")
    if not blocker or not blocked:
        raise HTTPException(400, "blocker_id and blocked_id required")
    if blocker == blocked:
        raise HTTPException(400, "Cannot block yourself")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id FROM blocks WHERE blocker_id=? AND blocked_id=?", (blocker, blocked))
    if c.fetchone():
        conn.close()
        raise HTTPException(400, "Already blocked")
    c.execute("INSERT INTO blocks (blocker_id, blocked_id) VALUES (?, ?)", (blocker, blocked))
    conn.commit()
    conn.close()
    log_activity(blocker, "blocked_user", blocked)
    return {"message": "User blocked"}

@router.post("/remove")
def remove_block(data: dict):
    blocker = data.get("blocker_id")
    blocked = data.get("blocked_id")
    if not blocker or not blocked:
        raise HTTPException(400, "blocker_id and blocked_id required")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM blocks WHERE blocker_id=? AND blocked_id=?", (blocker, blocked))
    conn.commit()
    conn.close()
    return {"message": "Block removed"}
