# Ludo & Snake Ladder Reward Platform

This project is a Python-based gaming platform with:
- User registration and login
- SQLite database persistence
- Ludo game logic
- Snake & Ladder gameplay
- Wallet and reward coins
- Leaderboard
- Admin dashboard
- Local multiplayer room support via Python sockets

## Features

- 2–4 player Ludo
- 2–4 player Snake & Ladder
- Secure password hashing
- Rewards and transaction tracking
- Global and weekly leaderboard scaffolding
- Reward redemption requests
- Admin controls to block users and review rewards
- Real SQLite data storage

## Tech Stack

- Python 3.10+
- Tkinter
- SQLite3
- Socket programming
- Pillow (installed for image support)
- Pygame (dependency included for future sound and visuals)

## Project Structure

```text
ludo-snake-earning-platform/
├── app/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── config.py
│   ├── database.py
│   ├── leaderboard.py
│   ├── rewards.py
│   ├── games/
│   │   ├── __init__.py
│   │   ├── ludo.py
│   │   └── snake_ladder.py
│   ├── networking/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── server.py
│   └── ui/
│       ├── __init__.py
│       ├── admin.py
│       └── dashboard.py
├── data/
│   └── platform.db
├── init_db.py
├── run.py
├── requirements.txt
├── sample_accounts.py
└── README.md
```

## Installation

1. Clone the repo.
2. Open the project folder in VS Code.
3. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Initialize the database:

```bash
python init_db.py
```

6. Start the app:

```bash
python run.py
```

## Sample Accounts

After running `python init_db.py`, sample accounts are created:

- admin / admin123
- player1 / player123
- player2 / player123
- player3 / player123

## Run in VS Code

1. Open the project folder in VS Code.
2. Select the Python interpreter from the virtual environment.
3. Open the terminal in VS Code.
4. Run:

```bash
python run.py
```

## Testing

- Register a user.
- Login with the created credentials.
- Play Ludo from the dashboard.
- Play Snake & Ladder from the dashboard.
- View wallet and transactions.
- Check leaderboard rankings.
- Admin login to review users and requests.

## Notes

- Coins are points only and are not real-world money.
- No gambling or wagering is implemented.
- Reward redemption requests are stored but require admin approval.

## License

MIT
