# routes/notifications.py
from fastapi import APIRouter
import sqlite3

router = APIRouter()
DB = "social.db"

@router.get("/user/{user_id}")
def get_notifications(user_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, text, seen, timestamp FROM notifications WHERE user_id=? ORDER BY timestamp DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    notifs = [{"id": r[0], "text": r[1], "seen": bool(r[2]), "timestamp": r[3]} for r in rows]
    return {"notifications": notifs}

@router.post("/seen/{notif_id}")
def mark_seen(notif_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE notifications SET seen=1 WHERE id=?", (notif_id,))
    conn.commit()
    conn.close()
    return {"message": "Marked seen"}
