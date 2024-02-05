# antihoag.py, a plugin that puts a player to spectators once he had reached the maximum consecutive number of wins (3).
import minqlx

class antihoag(minqlx.Plugin):
    def __init__(self):
        self.add_hook("game_end", self.handle_game_end)


        self.set_cvar_once("zmq_stats_enabled", "1")
        self.set_cvar("qlx_maxWinStreak", "3")
        self.maxWinStreak = int(self.get_cvar("qlx_maxWinStreak"))

        self.winner_id = 0
        self.winner_streak = 0


    def handle_game_end(self, data):
        if data["ABORTED"]: return
        scores = {}
        for player in self.players():
            if player.team != 'spectator':
                scores[player.steam_id] = player.score
        winner = max(scores, key=lambda k: scores[k])
        if winner == self.winner_id:
            self.winner_streak +=1
        else:
            self.winner_streak = 1
            self.winner_id = winner
        if self.winner_streak >= self.maxWinStreak:
            self.winner_streal = 0
            self.winner_id = 0
            for player in self.players():
                if player.steam_id == winner:
                    self.msg("{} has reached the winstreak limit of ^1{}^7 and has been put ^1back in line^7".format(player.name, self.maxWinStreak))
                    player.put('spectator')
