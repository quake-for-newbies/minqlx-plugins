import minqlx
import time
import os
import requests

VERSION = "v0.1"

class disable_ca(minqlx.Plugin):

    def __init__(self):
        self.add_hook("vote_called", self.handle_vote)

    def handle_vote(self, player, vote, args):
        if "ca".lower() in args.split(" "):
            player.tell('^1Clan Arena is not allowed on this server!')
            return minqlx.RET_STOP_ALL
