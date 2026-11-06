import hashlib
import secrets
import sqlite3
from datetime import datetime

from app.database import get_connection


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def _generate_salt() -> str:
    return secrets.token_hex(8)


def register_user(username: str, email: str, password: str, is_admin: bool = False):
    username = username.strip()
    if not username or not password:
        raise ValueError("Username and password are required.")

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if existing:
            raise ValueError("Username already exists.")

        salt = _generate_salt()
        password_hash = _hash_password(password, salt)
        referral_code = f"REF{secrets.token_hex(3).upper()}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = conn.execute(
            """
            INSERT INTO users (username, email, password_hash, salt, created_at, is_admin, referral_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (username, email or "", password_hash, salt, now, int(is_admin), referral_code),
        )
        user_id = cursor.lastrowid

        conn.execute(
            "INSERT INTO user_wallet (user_id, coins, total_earned, total_spent, updated_at) VALUES (?, 0, 0, 0, ?)",
            (user_id, now),
        )
        conn.commit()

        return {"id": user_id, "username": username, "email": email or "", "referral_code": referral_code}
    finally:
        conn.close()


def login_user(username: str, password: str):
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()
        if not user:
            return None

        if user["is_blocked"]:
            raise PermissionError("This account is blocked by admin.")

        if _hash_password(password, user["salt"]) != user["password_hash"]:
            return None

        conn.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user["id"]),
        )
        conn.commit()

        wallet = conn.execute(
            "SELECT coins FROM user_wallet WHERE user_id = ?",
            (user["id"],),
        ).fetchone()

        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "is_admin": bool(user["is_admin"]),
            "coins": wallet["coins"] if wallet else 0,
        }
    finally:
        conn.close()


def get_user_by_id(user_id: int):
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()


def forgot_password(username: str):
    conn = get_connection()
    try:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
        if not user:
            return None

        token = secrets.token_hex(16)
        conn.execute("UPDATE users SET reset_token = ? WHERE id = ?", (token, user["id"]))
        conn.commit()
        return token
    finally:
        conn.close()


def reset_password(token: str, new_password: str):
    if len(new_password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    conn = get_connection()
    try:
        user = conn.execute("SELECT * FROM users WHERE reset_token = ?", (token,)).fetchone()
        if not user:
            raise ValueError("Invalid reset token.")

        salt = _generate_salt()
        password_hash = _hash_password(new_password, salt)
        conn.execute(
            "UPDATE users SET password_hash = ?, salt = ?, reset_token = NULL WHERE id = ?",
            (password_hash, salt, user["id"]),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_all_users():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, username, email, is_admin, is_blocked, created_at FROM users ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def toggle_block_user(user_id: int, blocked: bool):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET is_blocked = ? WHERE id = ?",
            (int(blocked), user_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()
