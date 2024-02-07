import minqlx
import requests
import json
import threading
import socket
import re 

class discord_commands(minqlx.Plugin):

    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.set_cvar_once("qlx_discord_role_id", "")
        self.set_cvar_once("qlx_discord_lfg_channel_id", "")
        self.set_cvar_once("qlx_discord_bot_token", "")

        self.server_ip = s.getsockname()[0]
        self.discord_role_id = self.get_cvar("qlx_discord_role_id")
        self.discord_lfg_channel_id = self.get_cvar("qlx_discord_lfg_channel_id")
        self.discord_bot_token = self.get_cvar("qlx_discord_bot_token")

        self.add_hook("chat", self.handle_chat)

    @minqlx.thread
    def handle_chat(self, player, msg, channel):
        if self.discord_lfg_channel_id:
            if msg == "!promote":
                game_mode = self.game.type_short
                server_ip = self.server_ip + ":" + str(self.get_cvar("net_port"))
                role_id = int(self.get_cvar("qlx_discord_role_id"))  
                content = f"<@&{role_id}> | {self.strip_quake_colors(str(player))} is looking for {game_mode} [here](https://connectsteam.me/?{server_ip}) !!!"
                requests.post("https://discordapp.com/api/channels/" +  self.discord_lfg_channel_id + "/messages",
                                            data=json.dumps({'content': content}),
                                            headers = {'Content-type': 'application/json', 'Authorization': 'Bot ' + self.discord_bot_token})
                self.msg("^1Bot is summoning players from discord!")
    def strip_quake_colors(self, nickname):
        color_pattern = re.compile('\^[\d]')
        stripped_nickname = re.sub(color_pattern, '', nickname)

        return stripped_nickname