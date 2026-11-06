from app.auth_service import get_all_users, toggle_block_user
from app.rewards import get_redemption_requests, approve_redemption_request, deny_redemption_request


def admin_summary():
    users = get_all_users()
    requests = get_redemption_requests()
    return {
        "user_count": len(users),
        "blocked_count": sum(1 for u in users if u["is_blocked"]),
        "requests_count": len(requests),
    }
