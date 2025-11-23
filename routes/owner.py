from fastapi import APIRouter, HTTPException
import sqlite3

router = APIRouter(prefix="/owner", tags=["Owner"])
DB = "social.db"

def is_owner(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row and row[0] == "owner"

@router.post("/make-admin/{owner_id}/{user_id}")
def owner_make_admin(owner_id: int, user_id: int):
    if not is_owner(owner_id):
        raise HTTPException(status_code=403, detail="Only owner can make admins")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET role='admin' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return {"message": "Admin created"}

@router.post("/remove-admin/{owner_id}/{admin_id}")
def owner_remove_admin(owner_id: int, admin_id: int):
    if not is_owner(owner_id):
        raise HTTPException(status_code=403, detail="Only owner can remove admins")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET role='user' WHERE id=?", (admin_id,))
    conn.commit()
    conn.close()

    return {"message": "Admin removed"}
