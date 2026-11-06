import tkinter as tk
from tkinter import ttk, messagebox

from app.auth_service import login_user, register_user, get_all_users, toggle_block_user, reset_password, forgot_password
from app.rewards import get_wallet, get_transaction_history, grant_welcome_bonus, grant_daily_login_bonus, award_game_win, submit_redemption_request, get_redemption_requests, approve_redemption_request, deny_redemption_request
from app.games.ludo import LudoGame
from app.games.snake_ladder import SnakeLadderGame
from app.leaderboard import get_global_leaderboard
from app.networking.client import create_room, join_room, get_room_status


CURRENT_USER = None


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Ludo & Snake Rewards")
        self.root.geometry("420x420")
        self.root.configure(bg="#121826")

        tk.Label(root, text="Login / Register", font=("Arial", 20, "bold"), bg="#121826", fg="white").pack(pady=20)

        tk.Label(root, text="Username", bg="#121826", fg="white").pack()
        self.username = tk.Entry(root, width=30)
        self.username.pack(pady=5)

        tk.Label(root, text="Password", bg="#121826", fg="white").pack()
        self.password = tk.Entry(root, width=30, show="*")
        self.password.pack(pady=5)

        ttk.Button(root, text="Login", command=self.handle_login).pack(pady=8)
        ttk.Button(root, text="Register", command=self.handle_register).pack(pady=5)
        ttk.Button(root, text="Forgot Password", command=self.handle_forgot).pack(pady=5)

    def handle_login(self):
        global CURRENT_USER
        user = login_user(self.username.get(), self.password.get())
        if not user:
            messagebox.showerror("Login failed", "Invalid credentials.")
            return
        CURRENT_USER = user
        self.root.destroy()
        dashboard_root = tk.Tk()
        dashboard_root.geometry("1180x760")
        dashboard_root.configure(bg="#111827")
        DashboardWindow(dashboard_root, CURRENT_USER)
        dashboard_root.mainloop()

    def handle_register(self):
        try:
            register_user(self.username.get(), f"{self.username.get()}@example.com", self.password.get())
            messagebox.showinfo("Registration", "Account created successfully.")
            grant_welcome_bonus(login_user(self.username.get(), self.password.get())["id"])
        except Exception as exc:
            messagebox.showerror("Registration failed", str(exc))

    def handle_forgot(self):
        username = self.username.get().strip()
        if not username:
            messagebox.showerror("Forgot password", "Enter username first.")
            return
        token = forgot_password(username)
        if not token:
            messagebox.showerror("Forgot password", "User not found.")
            return
        new_password = simple_prompt("Reset Password", "Enter new password:")
        if new_password:
            try:
                reset_password(token, new_password)
                messagebox.showinfo("Password reset", "Password reset successful.")
            except Exception as exc:
                messagebox.showerror("Password reset failed", str(exc))


class DashboardWindow:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"Dashboard - {user['username']}")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.main_tab = ttk.Frame(self.notebook)
        self.wallet_tab = ttk.Frame(self.notebook)
        self.leaders_tab = ttk.Frame(self.notebook)
        self.multiplayer_tab = ttk.Frame(self.notebook)
        self.admin_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.main_tab, text="Home")
        self.notebook.add(self.wallet_tab, text="Wallet")
        self.notebook.add(self.leaders_tab, text="Leaderboard")
        self.notebook.add(self.multiplayer_tab, text="Multiplayer")
        if user["is_admin"]:
            self.notebook.add(self.admin_tab, text="Admin")

        self.render_home()
        self.render_wallet()
        self.render_leaders()
        self.render_multiplayer()
        if user["is_admin"]:
            self.render_admin()

    def render_home(self):
        tk.Label(self.main_tab, text=f"Welcome, {self.user['username']}", font=("Arial", 22, "bold")).pack(pady=10)
        ttk.Button(self.main_tab, text="Play Ludo", command=self.launch_ludo).pack(pady=8)
        ttk.Button(self.main_tab, text="Play Snake & Ladder", command=self.launch_snake_ladder).pack(pady=8)
        ttk.Button(self.main_tab, text="Daily Login Bonus", command=self.daily_bonus).pack(pady=8)
        ttk.Button(self.main_tab, text="Logout", command=self.logout).pack(pady=8)

    def render_wallet(self):
        wallet = get_wallet(self.user["id"])
        tk.Label(self.wallet_tab, text=f"Coins: {wallet['coins']}", font=("Arial", 17, "bold")).pack(pady=10)
        tk.Label(self.wallet_tab, text=f"Total Earned: {wallet['total_earned']}", font=("Arial", 12)).pack()
        tk.Label(self.wallet_tab, text=f"Total Spent: {wallet['total_spent']}", font=("Arial", 12)).pack()

        amount_var = tk.StringVar()
        tk.Label(self.wallet_tab, text="Redemption Amount").pack(pady=5)
        tk.Entry(self.wallet_tab, textvariable=amount_var).pack()
        ttk.Button(self.wallet_tab, text="Request Redemption", command=lambda: self.submit_redemption(amount_var.get())).pack(pady=10)

        txs = get_transaction_history(self.user["id"])
        list_box = tk.Listbox(self.wallet_tab, width=80, height=12)
        for tx in txs:
            list_box.insert("end", f"{tx['tx_type']} | {tx['amount']} | {tx['reason']} | {tx['created_at']}")
        list_box.pack(pady=10)

    def render_leaders(self):
        rows = get_global_leaderboard(10)
        list_box = tk.Listbox(self.leaders_tab, width=80, height=15)
        for index, row in enumerate(rows, start=1):
            list_box.insert("end", f"#{index} {row['username']} | wins={row['wins']} | games={row['total_games']} | score={row['score']}")
        list_box.pack(pady=20)

    def render_multiplayer(self):
        tk.Label(self.multiplayer_tab, text="Room Code").pack(pady=6)
        room_var = tk.StringVar()
        tk.Entry(self.multiplayer_tab, textvariable=room_var).pack()
        ttk.Button(self.multiplayer_tab, text="Create Room", command=lambda: self.create_multiplayer_room(room_var.get())).pack(pady=5)
        ttk.Button(self.multiplayer_tab, text="Join Room", command=lambda: self.join_multiplayer_room(room_var.get())).pack(pady=5)
        tk.Label(self.multiplayer_tab, text="Status: local socket room system is active").pack(pady=10)

    def render_admin(self):
        users = get_all_users()
        user_list = tk.Listbox(self.admin_tab, width=100, height=15)
        for user in users:
            status = "blocked" if user["is_blocked"] else "active"
            user_list.insert("end", f"{user['id']} | {user['username']} | {status}")
        user_list.pack(pady=10)

        def block_selected():
            selection = user_list.curselection()
            if not selection:
                return
            row = users[selection[0]]
            toggle_block_user(row["id"], not row["is_blocked"])
            messagebox.showinfo("Admin", f"Updated {row['username']}")
            self.root.update()

        ttk.Button(self.admin_tab, text="Toggle Block/Unblock Selected", command=block_selected).pack()

        redemptions = get_redemption_requests()
        red_list = tk.Listbox(self.admin_tab, width=100, height=10)
        for req in redemptions:
            red_list.insert("end", f"Request #{req['id']} | user={req['user_id']} | amount={req['amount']} | status={req['status']}")
        red_list.pack(pady=10)

        def approve_selected():
            selection = red_list.curselection()
            if not selection:
                return
            req = redemptions[selection[0]]
            approve_redemption_request(req["id"], self.user["username"])
            messagebox.showinfo("Approved", "Request approved.")

        def reject_selected():
            selection = red_list.curselection()
            if not selection:
                return
            req = redemptions[selection[0]]
            deny_redemption_request(req["id"], self.user["username"])
            messagebox.showinfo("Rejected", "Request rejected.")

        ttk.Button(self.admin_tab, text="Approve Selected", command=approve_selected).pack()
        ttk.Button(self.admin_tab, text="Reject Selected", command=reject_selected).pack()

    def launch_ludo(self):
        LudoWindow(self.root, self.user)

    def launch_snake_ladder(self):
        SnakeLadderWindow(self.root, self.user)

    def daily_bonus(self):
        if grant_daily_login_bonus(self.user["id"]):
            messagebox.showinfo("Bonus", "Daily login bonus awarded.")
        else:
            messagebox.showwarning("Bonus", "Bonus already processed or unavailable.")

    def submit_redemption(self, amount_text):
        try:
            amount = int(amount_text)
            submit_redemption_request(self.user["id"], amount)
            messagebox.showinfo("Request submitted", "Redemption request submitted for approval.")
        except Exception as exc:
            messagebox.showerror("Redemption failed", str(exc))

    def create_multiplayer_room(self, room_code):
        result = create_room(self.user["username"]) if not room_code else create_room(self.user["username"])
        if result.get("status") == "ok":
            messagebox.showinfo("Room created", f"Room code: {result['room_code']}")
        else:
            messagebox.showerror("Room error", result.get("message", "Unknown error"))

    def join_multiplayer_room(self, room_code):
        if not room_code:
            messagebox.showerror("Join room", "Enter room code.")
            return
        result = join_room(self.user["username"], room_code)
        if result.get("status") == "ok":
            messagebox.showinfo("Room joined", f"Joined room: {room_code}\nPlayers: {result['players']}")
        else:
            messagebox.showerror("Join failed", result.get("message", "Unknown error"))

    def logout(self):
        self.root.destroy()
        root = tk.Tk()
        LoginWindow(root)
        root.mainloop()


class LudoWindow(tk.Toplevel):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.title("Ludo")
        self.geometry("520x450")
        self.user = user
        self.game = LudoGame(["Player 1", "Player 2", "Player 3", "Player 4"])
        self.turn_label = tk.Label(self, text="Turn: Player 1")
        self.turn_label.pack(pady=5)
        self.output = tk.Text(self, height=12, width=55)
        self.output.pack(pady=5)
        self.roll_button = ttk.Button(self, text="Roll Dice", command=self.roll)
        self.roll_button.pack(pady=5)
        self.move_var = tk.StringVar(value="0")
        self.move_entry = tk.Entry(self, textvariable=self.move_var)
        self.move_entry.pack(pady=5)
        ttk.Button(self, text="Move Token", command=self.move).pack(pady=5)
        ttk.Button(self, text="Save result", command=self.save_result).pack(pady=5)
        self.log("Ludo started. Choose token number and roll a 6 to start.\n")

    def log(self, text):
        self.output.insert("end", text)
        self.output.see("end")

    def roll(self):
        value = self.game.roll_dice()
        self.log(f"Dice rolled: {value}\n")
        self.turn_label.config(text=f"Turn: {self.game.current_player_name()}")

    def move(self):
        try:
            dice_value = self.game.last_roll or int(self.move_var.get())
            token_index = int(self.move_var.get()) - 1
            if token_index < 0:
                raise ValueError("Use valid token index. ")
            result = self.game.move_token(self.game.current_player_name(), token_index, dice_value)
            self.log(f"Token moved to {result}\n")
            if self.game.winner:
                messagebox.showinfo("Winner", f"Winner is {self.game.winner}")
                award_game_win(self.user["id"], "Ludo", 100)
        except Exception as exc:
            self.log(f"Move failed: {exc}\n")

    def save_result(self):
        award_game_win(self.user["id"], "Ludo", 25)
        messagebox.showinfo("Saved", "Game result saved to wallet.")


class SnakeLadderWindow(tk.Toplevel):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.title("Snake & Ladder")
        self.geometry("520x420")
        self.user = user
        self.game = SnakeLadderGame(["Player 1", "Player 2", "Player 3", "Player 4"])
        self.label = tk.Label(self, text="Turn: Player 1")
        self.label.pack(pady=10)
        self.output = tk.Text(self, height=12, width=50)
        self.output.pack(pady=5)
        ttk.Button(self, text="Roll Dice", command=self.roll).pack(pady=5)
        ttk.Button(self, text="Complete Game Reward", command=self.reward).pack(pady=5)
        self.log("Snake and Ladder started.\n")

    def log(self, text):
        self.output.insert("end", text)
        self.output.see("end")

    def roll(self):
        value = self.game.roll_dice()
        self.log(f"Dice rolled: {value}\n")
        new_position = self.game.move_current_player(value)
        self.log(f"Current player moved to square {new_position}\n")
        self.label.config(text=f"Turn: {self.game.current_player_name()}")
        if self.game.winner:
            messagebox.showinfo("Winner", f"Winner: {self.game.winner}")
            award_game_win(self.user["id"], "Snake & Ladder", 100)

    def reward(self):
        award_game_win(self.user["id"], "Snake & Ladder", 20)
        messagebox.showinfo("Reward", "Winner reward added.")


def simple_prompt(title, message):
    popup = tk.Tk()
    popup.withdraw()
    answer = tk.simpledialog.askstring(title, message)
    popup.destroy()
    return answer


def launch_app():
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
