# crud.py
import sqlite3
import time

DB = "social.db"

def get_user_role(user_id: int) -> str:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id=?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else "user"

def log_activity(user_id: int, action: str, target_id: int = None):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO activity (user_id, action, target_id) VALUES (?, ?, ?)",
        (user_id, action, target_id),
    )
    conn.commit()
    # create a notification for all followers (simple)
    # fetch followers
    c.execute("SELECT follower_id FROM followers WHERE following_id=?", (user_id,))
    followers = [row[0] for row in c.fetchall()]
    for follower in followers:
        text = build_activity_text_simple(user_id, action, target_id)
        c.execute("INSERT INTO notifications (user_id, text) VALUES (?, ?)", (follower, text))
    conn.commit()
    conn.close()

def build_activity_text_simple(user_id, action, target_id):
    if action == "created_post":
        return f"User {user_id} created a post"
    if action == "liked_post":
        return f"User {user_id} liked post {target_id}"
    if action == "commented_post":
        return f"User {user_id} commented on post {target_id}"
    if action == "followed_user":
        return f"User {user_id} followed user {target_id}"
    return f"User {user_id} did {action}"
