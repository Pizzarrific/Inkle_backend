# routes/users.py
from fastapi import APIRouter, HTTPException
import sqlite3
import bcrypt
from crud import log_activity

router = APIRouter()   # <–– FIXED: removed prefix="/users"

DB = "social.db"


# ---------------------------------------------------
# Helper: Get user details
# ---------------------------------------------------
def get_user(user_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row


# ---------------------------------------------------
# SIGNUP
# ---------------------------------------------------
@router.post("/signup")
def signup(user: dict):
    username = user.get("username")
    password = user.get("password")

    if not username or not password:
        raise HTTPException(400, "Missing fields")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Check existing username
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        raise HTTPException(400, "Username already exists")

    # Hash password
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    c.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, 'user')",
        (username, hashed),
    )

    conn.commit()
    conn.close()

    return {"message": "User created successfully", "username": username}


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------
@router.post("/login")
def login(user: dict):
    username = user.get("username")
    password = user.get("password")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, username, password, role FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()

    if not row:
        raise HTTPException(404, "User not found")

    stored_hash = row[2]
    if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
        raise HTTPException(400, "Incorrect password")

    return {
        "message": "Login successful",
        "user_id": row[0],
        "username": row[1],
        "role": row[3]
    }


# ---------------------------------------------------
# ADMIN: Delete user
# ---------------------------------------------------
@router.delete("/admin/delete/{admin_id}/{target_id}")
def admin_delete_user(admin_id: int, target_id: int):
    admin = get_user(admin_id)

    if not admin:
        raise HTTPException(404, "Admin not found")

    if admin[2] not in ["admin", "owner"]:
        raise HTTPException(403, "Only admin/owner can delete users")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (target_id,))
    conn.commit()
    conn.close()

    # Log activity
    log_activity(admin_id, "admin_deleted_user", target_id)

    return {"message": "User deleted successfully"}


# ---------------------------------------------------
# OWNER: Promote user to Admin
# ---------------------------------------------------
@router.post("/owner/make-admin/{owner_id}/{user_id}")
def owner_make_admin(owner_id: int, user_id: int):
    owner = get_user(owner_id)

    if not owner:
        raise HTTPException(404, "Owner not found")

    if owner[2] != "owner":
        raise HTTPException(403, "Only owner can make admins")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET role='admin' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    log_activity(owner_id, "owner_created_admin", user_id)

    return {"message": "User promoted to admin"}


# ---------------------------------------------------
# OWNER: Remove Admin role
# ---------------------------------------------------
@router.post("/owner/remove-admin/{owner_id}/{admin_id}")
def owner_remove_admin(owner_id: int, admin_id: int):
    owner = get_user(owner_id)

    if not owner or owner[2] != "owner":
        raise HTTPException(403, "Only owner can remove admin")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET role='user' WHERE id=?", (admin_id,))
    conn.commit()
    conn.close()

    log_activity(owner_id, "owner_removed_admin", admin_id)

    return {"message": "Admin demoted to user"}
