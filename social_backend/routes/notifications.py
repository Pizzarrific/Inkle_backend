from fastapi import APIRouter
import sqlite3

router = APIRouter(prefix="/notifications", tags=["Notifications"])

DB = "social.db"


# ----------------------------
# GET notifications for user
# ----------------------------
@router.get("/{user_id}")
def get_notifications(user_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        SELECT id, type, from_user, post_id, seen, created_at
        FROM notifications
        WHERE user_id=?
        ORDER BY created_at DESC
    """, (user_id,))

    rows = c.fetchall()
    conn.close()

    notifications = [
        {
            "id": r[0],
            "type": r[1],
            "from_user": r[2],
            "post_id": r[3],
            "seen": r[4],
            "created_at": r[5]
        }
        for r in rows
    ]

    return {"notifications": notifications}


# ----------------------------
# MARK AS SEEN
# ----------------------------
@router.post("/seen/{notif_id}")
def mark_seen(notif_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("UPDATE notifications SET seen=1 WHERE id=?", (notif_id,))
    conn.commit()
    conn.close()

    return {"message": "Notification marked as seen"}
