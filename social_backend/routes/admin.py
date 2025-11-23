# routes/admin.py

from fastapi import APIRouter, HTTPException
import sqlite3
from crud import get_user_role, log_activity

DB = "social.db"
router = APIRouter(prefix="/admin", tags=["Admin"])


# ---------------------------------------------------------
# DELETE POST (Admin + Owner)
# ---------------------------------------------------------
@router.delete("/delete_post")
def delete_post(data: dict):
    admin_id = data.get("admin_id")
    post_id = data.get("post_id")

    if not admin_id or not post_id:
        raise HTTPException(400, "admin_id and post_id are required")

    role = get_user_role(admin_id)

    if role not in ("admin", "owner"):
        raise HTTPException(403, "Only admins or owners can delete posts")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Check if post exists
    c.execute("SELECT id FROM posts WHERE id=?", (post_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(404, "Post not found")

    # Delete post
    c.execute("DELETE FROM posts WHERE id=?", (post_id,))
    conn.commit()
    conn.close()

    # Log activity
    log_activity(admin_id, "admin_deleted_post", post_id)

    return {"message": "Post deleted successfully"}


# ---------------------------------------------------------
# DELETE USER (Admin + Owner)
# Admin cannot delete admin or owner
# Owner cannot delete another owner
# ---------------------------------------------------------
@router.delete("/delete_user")
def delete_user(data: dict):
    admin_id = data.get("admin_id")
    target_id = data.get("target_id")

    if not admin_id or not target_id:
        raise HTTPException(400, "admin_id and target_id are required")

    admin_role = get_user_role(admin_id)
    target_role = get_user_role(target_id)

    if admin_role not in ("admin", "owner"):
        raise HTTPException(403, "Only admins or owners can delete users")

    # Admin cannot delete admin or owner
    if admin_role == "admin" and target_role in ("admin", "owner"):
        raise HTTPException(403, "Admins cannot delete admins or owners")

    # Owner cannot delete owner
    if admin_role == "owner" and target_role == "owner":
        raise HTTPException(403, "Owner cannot delete another owner")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Clean related data (posts, likes, comments, follows, blocks)
    c.execute("DELETE FROM posts WHERE user_id=?", (target_id,))
    c.execute("DELETE FROM likes WHERE user_id=?", (target_id,))
    c.execute("DELETE FROM comments WHERE user_id=?", (target_id,))
    c.execute("DELETE FROM followers WHERE follower_id=? OR following_id=?", (target_id, target_id))
    c.execute("DELETE FROM blocks WHERE blocker_id=? OR blocked_id=?", (target_id, target_id))

    # Delete user
    c.execute("DELETE FROM users WHERE id=?", (target_id,))
    conn.commit()
    conn.close()

    log_activity(admin_id, "admin_deleted_user", target_id)

    return {"message": "User deleted successfully"}


# ---------------------------------------------------------
# OWNER MAKES ADMIN
# ---------------------------------------------------------
@router.post("/make_admin")
def make_admin(data: dict):
    owner_id = data.get("owner_id")
    target_id = data.get("target_id")

    if not owner_id or not target_id:
        raise HTTPException(400, "owner_id and target_id are required")

    role = get_user_role(owner_id)
    if role != "owner":
        raise HTTPException(403, "Only owner can make someone admin")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET role='admin' WHERE id=?", (target_id,))
    conn.commit()
    conn.close()

    log_activity(owner_id, "owner_created_admin", target_id)

    return {"message": "User promoted to admin"}


# ---------------------------------------------------------
# OWNER REMOVES ADMIN ROLE
# ---------------------------------------------------------
@router.post("/remove_admin")
def remove_admin(data: dict):
    owner_id = data.get("owner_id")
    target_id = data.get("target_id")

    if not owner_id or not target_id:
        raise HTTPException(400, "owner_id and target_id are required")

    role = get_user_role(owner_id)
    if role != "owner":
        raise HTTPException(403, "Only owner can remove admin role")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET role='user' WHERE id=?", (target_id,))
    conn.commit()
    conn.close()

    log_activity(owner_id, "owner_removed_admin", target_id)

    return {"message": "Admin rights removed successfully"}
