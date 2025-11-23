# social_backend/routes/block.py
from fastapi import APIRouter, HTTPException
import sqlite3
from crud import log_activity

router = APIRouter(prefix="/block", tags=["Block"])
DB = "social.db"

def init_block_table():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blocker_id INTEGER,
            blocked_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """); conn.commit(); conn.close()

init_block_table()

@router.post("/add")
def add_block(data: dict):
    blocker = data.get("blocker_id"); blocked = data.get("blocked_id")
    if not blocker or not blocked:
        raise HTTPException(status_code=400, detail="Missing blocker_id/blocked_id")
    if blocker == blocked:
        raise HTTPException(status_code=400, detail="Cannot block yourself")
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT id FROM blocks WHERE blocker_id=? AND blocked_id=?", (blocker, blocked))
    if c.fetchone():
        conn.close(); raise HTTPException(status_code=400, detail="Already blocked")
    c.execute("INSERT INTO blocks (blocker_id, blocked_id) VALUES (?, ?)", (blocker, blocked))
    conn.commit(); conn.close()
    log_activity(blocker, "blocked_user", blocked)
    return {"message": "User blocked"}

@router.post("/remove")
def remove_block(data: dict):
    blocker = data.get("blocker_id"); blocked = data.get("blocked_id")
    if not blocker or not blocked:
        raise HTTPException(status_code=400, detail="Missing blocker_id/blocked_id")
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("DELETE FROM blocks WHERE blocker_id=? AND blocked_id=?", (blocker, blocked))
    conn.commit(); conn.close()
    return {"message": "User unblocked"}
