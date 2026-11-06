import random


LADDERS = {
    3: 22,
    10: 28,
    18: 41,
    28: 77,
    45: 62,
    52: 81,
    71: 92,
    80: 99,
}

SNAKES = {
    17: 7,
    33: 15,
    49: 32,
    57: 36,
    76: 54,
    88: 67,
    95: 74,
    98: 18,
}


class SnakeLadderGame:
    def __init__(self, players):
        self.players = [{"name": name, "position": 0} for name in players]
        self.turn_index = 0
        self.last_roll = 0
        self.winner = None

    def roll_dice(self):
        self.last_roll = random.randint(1, 6)
        return self.last_roll

    def move_current_player(self, dice_value):
        player = self.players[self.turn_index]
        target = player["position"] + dice_value
        if target > 100:
            target = player["position"]
        else:
            player["position"] = target
            if target in LADDERS:
                player["position"] = LADDERS[target]
            elif target in SNAKES:
                player["position"] = SNAKES[target]

        if player["position"] == 100:
            self.winner = player["name"]
        else:
            self.turn_index = (self.turn_index + 1) % len(self.players)

        return player["position"]

    def current_player_name(self):
        return self.players[self.turn_index]["name"]

    def snapshot(self):
        return {
            "turn_index": self.turn_index,
            "winner": self.winner,
            "players": self.players,
            "last_roll": self.last_roll,
        }
