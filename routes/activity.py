# routes/activity.py
from fastapi import APIRouter
import sqlite3

router = APIRouter()
DB = "social.db"

# viewer_id sees feed (hide activities by users the viewer has blocked,
# also hide activities from users that viewer blocked? spec: hide activities involving blocked users for a viewer)
@router.get("/{viewer_id}")
def get_activity_feed(viewer_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # users that viewer has blocked (viewer blocked => don't show blocked users' posts to viewer)
    c.execute("SELECT blocked_id FROM blocks WHERE blocker_id=?", (viewer_id,))
    blocked_users = {r[0] for r in c.fetchall()}
    # get activities
    c.execute("""
        SELECT a.id, a.user_id, a.action, a.target_id, a.timestamp, u.username
        FROM activity a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.timestamp DESC
    """)
    rows = c.fetchall()
    conn.close()
    out = []
    for r in rows:
        user_id = r[1]
        if user_id in blocked_users:
            continue
        out.append({
            "id": r[0],
            "user_id": r[1],
            "action": r[2],
            "target_id": r[3],
            "timestamp": r[4],
            "username": r[5],
            "text": format_activity_text(r)
        })
    return {"feed": out}

def format_activity_text(row):
    action = row[2]
    username = row[5]
    target = row[3]
    if action == "created_post":
        return f"{username} made a post"
    if action == "liked_post":
        return f"{username} liked post #{target}"
    if action == "commented_post":
        return f"{username} commented on post #{target}"
    if action == "followed_user":
        return f"{username} followed user #{target}"
    if action == "blocked_user":
        return f"{username} blocked user #{target}"
    if action == "admin_deleted_post":
        return f"Admin deleted post #{target}"
    if action == "admin_deleted_user":
        return f"Admin deleted user #{target}"
    if action == "owner_created_admin":
        return f"Owner made user #{target} an admin"
    if action == "owner_removed_admin":
        return f"Owner removed admin privileges from user #{target}"
    return f"{username} performed {action}"
