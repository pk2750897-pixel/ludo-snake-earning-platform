import sqlite3
from pathlib import Path

from app.config import DB_PATH, DATA_DIR


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT,
            is_admin INTEGER DEFAULT 0,
            is_blocked INTEGER DEFAULT 0,
            referral_code TEXT,
            reset_token TEXT
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_wallet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            coins INTEGER DEFAULT 0,
            total_earned INTEGER DEFAULT 0,
            total_spent INTEGER DEFAULT 0,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tx_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            reason TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_name TEXT NOT NULL,
            result TEXT NOT NULL,
            won INTEGER DEFAULT 0,
            coins_awarded INTEGER DEFAULT 0,
            played_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_user_id INTEGER NOT NULL,
            referred_user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(referrer_user_id) REFERENCES users(id),
            FOREIGN KEY(referred_user_id) REFERENCES users(id)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS redemption_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            reviewed_by TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            wins INTEGER DEFAULT 0,
            total_games INTEGER DEFAULT 0,
            score INTEGER DEFAULT 0,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    conn.commit()
    conn.close()

    _seed_sample_accounts()


def _seed_sample_accounts():
    from app.auth_service import register_user
    from app.rewards import grant_welcome_bonus

    profiles = [
        ("admin", "admin@example.com", "admin123", True),
        ("player1", "player1@example.com", "player123", False),
        ("player2", "player2@example.com", "player123", False),
        ("player3", "player3@example.com", "player123", False),
    ]

    for username, email, password, is_admin in profiles:
        try:
            user = register_user(username, email, password, is_admin=is_admin)
            grant_welcome_bonus(user["id"])
        except Exception:
            pass
