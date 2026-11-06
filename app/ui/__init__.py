from app.auth_service import register_user, login_user
from app.rewards import grant_welcome_bonus

if __name__ == "__main__":
    sample_users = [
        ("admin", "admin@example.com", "admin123", True),
        ("player1", "player1@example.com", "player123", False),
        ("player2", "player2@example.com", "player123", False),
        ("player3", "player3@example.com", "player123", False),
    ]

    for username, email, password, is_admin in sample_users:
        try:
            user = register_user(username, email, password, is_admin=is_admin)
            grant_welcome_bonus(user["id"])
            print(f"Created account: {username}")
        except Exception as exc:
            print(f"Account {username} likely already exists. {exc}")

    print("Login check:", login_user("player1", "player123"))
