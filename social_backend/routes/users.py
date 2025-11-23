# routes/users.py
from fastapi import APIRouter, HTTPException
import sqlite3
import bcrypt
from crud import log_activity

router = APIRouter()
DB = "social.db"

def get_user_raw(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users WHERE id=?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r

@router.post("/signup")
def signup(user: dict):
    username = user.get("username")
    password = user.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing fields")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username exists")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    log_activity(user_id, "created_profile", None)
    return {"message": "User created", "user_id": user_id}

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
        raise HTTPException(status_code=404, detail="User not found")
    stored_hash = row[2]
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return {"message": "Login successful", "user_id": row[0], "username": row[1], "role": row[3]}

# Admin delete user route (owner/admin)
@router.delete("/admin/delete/{admin_id}/{target_id}")
def admin_delete(admin_id: int, target_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id=?", (admin_id,))
    r = c.fetchone()
    if not r:
        conn.close()
        raise HTTPException(status_code=404, detail="Admin not found")
    if r[0] not in ("admin", "owner"):
        conn.close()
        raise HTTPException(status_code=403, detail="Not permitted")
    # delete user and related items (simple cleanup)
    c.execute("DELETE FROM posts WHERE user_id=?", (target_id,))
    c.execute("DELETE FROM likes WHERE user_id=?", (target_id,))
    c.execute("DELETE FROM comments WHERE user_id=?", (target_id,))
    c.execute("DELETE FROM followers WHERE follower_id=? OR following_id=?", (target_id, target_id))
    c.execute("DELETE FROM blocks WHERE blocker_id=? OR blocked_id=?", (target_id, target_id))
    c.execute("DELETE FROM users WHERE id=?", (target_id,))
    conn.commit()
    conn.close()
    log_activity(admin_id, "admin_deleted_user", target_id)
    return {"message": "User deleted"}

@router.post("/owner/make-admin/{owner_id}/{user_id}")
def owner_make_admin(owner_id: int, user_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id=?", (owner_id,))
    r = c.fetchone()
    if not r or r[0] != "owner":
        conn.close()
        raise HTTPException(status_code=403, detail="Only owner")
    c.execute("UPDATE users SET role='admin' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    log_activity(owner_id, "owner_created_admin", user_id)
    return {"message": "Promoted to admin"}

@router.post("/owner/remove-admin/{owner_id}/{admin_id}")
def owner_remove_admin(owner_id: int, admin_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id=?", (owner_id,))
    r = c.fetchone()
    if not r or r[0] != "owner":
        conn.close()
        raise HTTPException(status_code=403, detail="Only owner")
    c.execute("UPDATE users SET role='user' WHERE id=?", (admin_id,))
    conn.commit()
    conn.close()
    log_activity(owner_id, "owner_removed_admin", admin_id)
    return {"message": "Admin removed"}
