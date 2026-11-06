import random


class LudoGame:
    PLAYER_COLORS = ["red", "green", "yellow", "blue"]

    def __init__(self, players):
        self.players = []
        for index, name in enumerate(players):
            self.players.append({
                "name": name,
                "color": self.PLAYER_COLORS[index % len(self.PLAYER_COLORS)],
                "tokens": [-1, -1, -1, -1],
                "finished": 0,
            })
        self.turn_index = 0
        self.last_roll = 0
        self.winner = None

    def roll_dice(self):
        self.last_roll = random.randint(1, 6)
        return self.last_roll

    def valid_moves(self, player_name, dice_value):
        player = self._get_player(player_name)
        valid = []
        for idx, token in enumerate(player["tokens"]):
            if token == -1:
                if dice_value == 6:
                    valid.append(idx)
            elif token < 57 and token + dice_value <= 57:
                valid.append(idx)
        return valid

    def move_token(self, player_name, token_index, dice_value):
        player = self._get_player(player_name)
        current = player["tokens"][token_index]

        if current == -1:
            if dice_value != 6:
                raise ValueError("Token must start with a 6.")
            player["tokens"][token_index] = 0
        else:
            if current + dice_value > 57:
                raise ValueError("Move exceeds finish lane.")
            player["tokens"][token_index] += dice_value

        self._handle_capture(player_name, token_index)
        if player["tokens"][token_index] == 57:
            player["finished"] += 1

        if all(token == 57 for token in player["tokens"]):
            self.winner = player_name
        else:
            self.turn_index = (self.turn_index + 1) % len(self.players)

        return player["tokens"][token_index]

    def _handle_capture(self, player_name, token_index):
        player = self._get_player(player_name)
        position = player["tokens"][token_index]
        if position < 0:
            return

        for other in self.players:
            if other["name"] == player_name:
                continue
            for idx, token in enumerate(other["tokens"]):
                if token == position and position not in (-1, 57):
                    other["tokens"][idx] = -1

    def _get_player(self, name):
        for player in self.players:
            if player["name"] == name:
                return player
        raise ValueError(f"Player not found: {name}")

    def current_player_name(self):
        return self.players[self.turn_index]["name"]

    def snapshot(self):
        return {
            "turn_index": self.turn_index,
            "winner": self.winner,
            "players": self.players,
            "last_roll": self.last_roll,
        }
