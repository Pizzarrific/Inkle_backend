# social_backend/routes/activity.py
from fastapi import APIRouter, Query
import sqlite3
from crud import is_blocked_between

router = APIRouter(prefix="/activity", tags=["Activity"])
DB = "social.db"

def get_username(user_id):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id=?", (user_id,)); r = c.fetchone(); conn.close()
    return r[0] if r else "Unknown"

@router.get("/all")
def get_all(viewer_id: int = Query(None), limit: int = Query(100), offset: int = Query(0)):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("""
        SELECT activity.id, activity.user_id, activity.action, activity.target_id, activity.timestamp
        FROM activity ORDER BY activity.timestamp DESC LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = c.fetchall(); conn.close()
    formatted = []
    for act_id, actor_id, action, target_id, ts in rows:
        if viewer_id and is_blocked_between(viewer_id, actor_id):
            continue
        # Format text
        actor = get_username(actor_id)
        if action == "created_post":
            text = f"{actor} made a post"
        elif action == "liked_post":
            # target_id is post_id -> find owner
            conn = sqlite3.connect(DB); c = conn.cursor()
            c.execute("SELECT users.username FROM posts JOIN users ON posts.user_id=users.id WHERE posts.id=?", (target_id,))
            r = c.fetchone(); conn.close()
            owner = r[0] if r else "Unknown"
            if viewer_id and is_blocked_between(viewer_id, actor_id):
                continue
            text = f"{actor} liked {owner}'s post"
        elif action == "commented_post":
            conn = sqlite3.connect(DB); c = conn.cursor()
            c.execute("SELECT users.username FROM posts JOIN users ON posts.user_id=users.id WHERE posts.id=?", (target_id,))
            r = c.fetchone(); conn.close()
            owner = r[0] if r else "Unknown"
            text = f"{actor} commented on {owner}'s post"
        elif action == "followed_user":
            followed = get_username(target_id)
            text = f"{actor} followed {followed}"
        elif action in ("user_deleted_by_owner","user_deleted_by_admin"):
            target_name = get_username(target_id)
            text = f"{actor} deleted user {target_name}"
        elif action in ("post_deleted_by_admin","post_deleted_by_owner"):
            text = f"{actor} deleted a post"
        elif action == "blocked_user":
            target_name = get_username(target_id)
            text = f"{actor} blocked {target_name}"
        else:
            text = f"{actor} performed {action}"
        formatted.append({"id": act_id, "text": text, "timestamp": ts})
    return {"activity": formatted}
