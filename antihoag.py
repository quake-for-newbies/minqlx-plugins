import minqlx

class antihoag(minqlx.Plugin):
  def __init__(self):
      self.add_hook("game_end", self.handle_game_end)
      self.add_hook("player_spawn", self.handle_player_spawn)

      self.set_cvar_once("qlx_maxWinStreak", "3")

      self.winner_id = 0
      self.winner_streak = 0

  def handle_game_end(self, *args, **kwargs):
      scores = {}
      for player in self.players():
        scores[player.steam_id] = player.score
      winner = max(scores, key=lambda k: scores[k])
      if winner:
        self.winner_id = winner.steam_id
        self.winner_streak += 1

  def handle_player_spawn(self, player):
      if self.get_cvar("qlx_maxWinStreak") > 0 and self.winner_streak >= self.get_cvar("qlx_maxWinStreak") and player.steam_id == self.winner_id:
        player.put('spectator')
        self.winner_streak = 0
        self.msg("{} has reached the consecutive win limit of {} and has been moved to spectators."
                 .format(player.name, self.get_cvar("qlx_maxWinStreak")))
