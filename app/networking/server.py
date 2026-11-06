from datetime import datetime

from app.database import get_connection


def rebuild_leaderboard():
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT user_id, SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) AS wins,
                   COUNT(*) AS total_games,
                   SUM(coins_awarded) AS score
            FROM game_history
            GROUP BY user_id
            """
        ).fetchall()

        for row in rows:
            conn.execute(
                """
                INSERT INTO leaderboard (user_id, wins, total_games, score, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET wins=excluded.wins, total_games=excluded.total_games, score=excluded.score, updated_at=excluded.updated_at
                """,
                (row["user_id"], row["wins"], row["total_games"], row["score"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )

        conn.commit()
        return True
    finally:
        conn.close()


def get_global_leaderboard(limit: int = 10):
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT u.username, l.wins, l.total_games, l.score
            FROM leaderboard l
            INNER JOIN users u ON u.id = l.user_id
            ORDER BY l.score DESC, l.wins DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
