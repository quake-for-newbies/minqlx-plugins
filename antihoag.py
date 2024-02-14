# antihoag.py, a plugin that puts a player to spectators once he had reached the maximum consecutive number of wins (3).
import minqlx


class antihoag(minqlx.Plugin):
    def __init__(self):
        self.add_hook("game_end", self.handle_game_end)

        self.set_cvar("qlx_maxWinStreak", "3")

        self.winner_id = -1
        self.winner_streak = 0

        self.scores = {}
        self.winner = 0

    @minqlx.delay(0.25)
    def handle_game_end(self, data):
        if data["ABORTED"]:
            return minqlx.RET_NONE
        self.scores = {}

        for player in self.players():
            if player.team != "spectator":
                self.scores[player.steam_id] = player.score
        if self.scores:
            self.winner = max(self.scores, key=lambda k: self.scores[k])
        if self.winner == self.winner_id:
            self.winner_streak += 1
        else:
            self.winner_streak = 1
            self.winner_id = self.winner
        if self.winner_streak >= int(self.get_cvar("qlx_maxWinStreak")):
            self.winner_streak = 0
            self.winner_id = 0
            for player in self.players():
                if player.steam_id == self.winner:
                    self.msg(
                        "{} has reached the winstreak limit of ^1{}^7 and has been put ^1back in line^7".format(
                            player.name, int(self.get_cvar("qlx_maxWinStreak"))
                        )
                    )
                    player.put("spectator")
        return minqlx.RET_NONE
