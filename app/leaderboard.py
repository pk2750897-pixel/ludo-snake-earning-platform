from datetime import datetime

from app.database import get_connection


def add_transaction(user_id: int, tx_type: str, amount: int, reason: str):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO transactions (user_id, tx_type, amount, reason, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, tx_type, amount, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
    finally:
        conn.close()


def get_wallet(user_id: int):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM user_wallet WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            return {"coins": 0, "total_earned": 0, "total_spent": 0}
        return dict(row)
    finally:
        conn.close()


def get_transaction_history(user_id: int):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC LIMIT 20",
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def award_coins(user_id: int, amount: int, reason: str):
    if amount <= 0:
        return False

    conn = get_connection()
    try:
        wallet = conn.execute("SELECT * FROM user_wallet WHERE user_id = ?", (user_id,)).fetchone()
        if wallet is None:
            conn.execute(
                "INSERT INTO user_wallet (user_id, coins, total_earned, total_spent, updated_at) VALUES (?, ?, ?, 0, ?)",
                (user_id, amount, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
        else:
            new_coins = wallet["coins"] + amount
            new_total = wallet["total_earned"] + amount
            conn.execute(
                "UPDATE user_wallet SET coins = ?, total_earned = ?, updated_at = ? WHERE user_id = ?",
                (new_coins, new_total, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
            )

        conn.execute(
            "INSERT INTO transactions (user_id, tx_type, amount, reason, created_at) VALUES (?, 'credit', ?, ?, ?)",
            (user_id, amount, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def deduct_coins(user_id: int, amount: int, reason: str):
    if amount <= 0:
        return False

    conn = get_connection()
    try:
        wallet = conn.execute("SELECT * FROM user_wallet WHERE user_id = ?", (user_id,)).fetchone()
        if wallet is None or wallet["coins"] < amount:
            return False

        new_coins = wallet["coins"] - amount
        new_total_spent = wallet["total_spent"] + amount
        conn.execute(
            "UPDATE user_wallet SET coins = ?, total_spent = ?, updated_at = ? WHERE user_id = ?",
            (new_coins, new_total_spent, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
        )
        conn.execute(
            "INSERT INTO transactions (user_id, tx_type, amount, reason, created_at) VALUES (?, 'debit', ?, ?, ?)",
            (user_id, amount, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def grant_welcome_bonus(user_id: int):
    return award_coins(user_id, 50, "Welcome bonus")


def grant_daily_login_bonus(user_id: int):
    return award_coins(user_id, 25, "Daily login bonus")


def award_game_win(user_id: int, game_name: str, bonus: int):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO game_history (user_id, game_name, result, won, coins_awarded, played_at) VALUES (?, ?, ?, 1, ?, ?)",
            (user_id, game_name, "win", bonus, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
    finally:
        conn.close()
    return award_coins(user_id, bonus, f"Winner bonus for {game_name}")


def award_game_loss(user_id: int, game_name: str):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO game_history (user_id, game_name, result, won, coins_awarded, played_at) VALUES (?, ?, ?, 0, 0, ?)",
            (user_id, game_name, "loss", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
    finally:
        conn.close()
    return True


def submit_redemption_request(user_id: int, amount: int):
    if amount <= 0:
        raise ValueError("Amount must be positive.")

    wallet = get_wallet(user_id)
    if wallet["coins"] < amount:
        raise ValueError("Insufficient coins for redemption request.")

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO redemption_requests (user_id, amount, status, created_at) VALUES (?, ?, 'pending', ?)",
            (user_id, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def approve_redemption_request(request_id: int, reviewed_by: str):
    conn = get_connection()
    try:
        request = conn.execute("SELECT * FROM redemption_requests WHERE id = ?", (request_id,)).fetchone()
        if not request:
            return False
        conn.execute(
            "UPDATE redemption_requests SET status = 'approved', reviewed_by = ? WHERE id = ?",
            (reviewed_by, request_id),
        )
        conn.commit()
        deduct_coins(request["user_id"], request["amount"], "Redemption approved")
        return True
    finally:
        conn.close()


def deny_redemption_request(request_id: int, reviewed_by: str):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE redemption_requests SET status = 'rejected', reviewed_by = ? WHERE id = ?",
            (reviewed_by, request_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_redemption_requests():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM redemption_requests ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
