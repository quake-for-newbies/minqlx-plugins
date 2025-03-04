import minqlx
import requests
import json
import threading
import socket
import re
import time

class discord_commands(minqlx.Plugin):

    def __init__(self):
        super().__init__()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.set_cvar_once("qlx_discord_role_id", "")
        self.set_cvar_once("qlx_discord_lfg_channel_id", "")
        self.set_cvar_once("qlx_discord_bot_token", "")

        self.server_ip = s.getsockname()[0]
        self.sv_hostname = self.get_cvar("sv_hostname")
        self.discord_role_id = self.get_cvar("qlx_discord_role_id")
        self.discord_lfg_channel_id = self.get_cvar("qlx_discord_lfg_channel_id")
        self.discord_bot_token = self.get_cvar("qlx_discord_bot_token")

        self.discord_game_state = ""

        self.cooldown_time = 600  # 10 minutes cooldown in seconds
        self.last_promote_time = 0

        self.add_hook("chat", self.handle_chat)

    def handle_chat(self, player, msg, channel):
        if self.discord_lfg_channel_id:
            if msg == "!promote":
                self.discord_game_state = self.get_cvar("g_gamestate")
                if not self.discord_game_state == "IN_PROGRESS":
                    current_time = time.time()
                    if current_time - self.last_promote_time >= self.cooldown_time:
                        game_mode = self.game.type_short
                        sv_hostname = self.sv_hostname
                        server_ip = self.server_ip + ":" + str(self.get_cvar("net_port"))
                        role_id = int(self.get_cvar("qlx_discord_role_id"))
                        target_elo = self.fetch(player)
                        content = f"<@&{role_id}> | {self.strip_quake_colors(str(player))} (ELO : {target_elo['elo']}, {target_elo['games']} games) is looking for {game_mode} on [{sv_hostname}](https://quakenewbies.com/connect/{server_ip}) !!!"
                        req = requests.post("https://discordapp.com/api/channels/" +  self.discord_lfg_channel_id + "/messages",
                                                    data=json.dumps({'content': content}),
                                                    headers={'Content-type': 'application/json', 'Authorization': 'Bot ' + self.discord_bot_token})
                        if req.status_code == 200:
                            self.msg("^1Bot is summoning players from discord!")
                            self.last_promote_time = current_time  # Update last promote time
                        else:
                            self.msg(f"^1Bot couldn't reach Discord, status code ^2{req.status_code}")
                    else:
                        remaining_time = int(self.cooldown_time - (current_time - self.last_promote_time))
                        self.msg("^1You can promote again in {} minutes.".format(round(remaining_time / 60), 1))
                else:
                    self.msg("^1You can't use ^6!promote ^1if a game is being played.")
    def strip_quake_colors(self, nickname):
        color_pattern = re.compile('\^[\d]')
        stripped_nickname = re.sub(color_pattern, '', nickname)

        return stripped_nickname
        
    def fetch(self, player):
        gt = self.game.type_short
        try:
            sid = player.steam_id
        except:
            sid = player

        attempts = 0
        last_status = 0
        while attempts < 3:
            attempts += 1
            url = "http://qlstats.net/{elo}/{}".format(sid, elo=self.get_cvar('qlx_balanceApi'))
            res = requests.get(url)
            last_status = res.status_code
            if res.status_code != requests.codes.ok:
                continue

            js = res.json()
            if "players" not in js:
                last_status = -1
                continue

            for p in js["players"]:
                _sid = int(p["steamid"])
                if _sid == sid: # got our player
                    if gt not in p:
                        print("echo No {} rating for {}".format(gt, _sid))
                        print("no stats")

                    _gt = p[gt]
                    return _gt

            # If our players has not been found yet, then he is not known in the system
            _gt['elo'] = 0
            _gt['games'] = 0
            return _gt


        self.msg("^1echo Problem fetching {} glicko: {}".format(gt, last_status))
        return
