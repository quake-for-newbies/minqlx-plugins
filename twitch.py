# minqlx - A Quake Live server administrator bot.
# Copyright (C) 2015 Mino <mino@minomino.org>

# This file is part of minqlx.

# minqlx is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# minqlx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

import minqlx
import threading
import asyncio
import random
import time
import re

# Colors using the mIRC color standard palette (which several other clients also comply with).
COLORS = ("\x0301", "\x0304", "\x0303", "\x0308", "\x0302", "\x0311", "\x0306", "\x0300")

class twitch(minqlx.Plugin):
    def __init__(self):
        self.add_hook("chat", self.handle_chat, priority=minqlx.PRI_LOWEST)
        self.add_hook("unload", self.handle_unload)

        self.set_cvar_once("qlx_ircServer", "irc.twitch.tv")
        self.set_cvar_once("qlx_ircRelayChannel", "")
        self.set_cvar_once("qlx_ircRelayIrcChat", "1")
        self.set_cvar_once("qlx_ircNickname", "")
        self.set_cvar_once("qlx_ircPassword", "")
        self.set_cvar_once("qlx_ircColors", "0")

        self.server = self.get_cvar("qlx_ircServer")
        self.relay = self.get_cvar("qlx_ircRelayChannel")
        self.nickname = self.get_cvar("qlx_ircNickname")
        self.password = self.get_cvar("qlx_ircPassword")
        self.is_relaying = self.get_cvar("qlx_ircRelayIrcChat", bool)

        self.authed = set()
        self.auth_attempts = {}

        if not self.server:
            self.logger.warning("IRC plugin loaded, but no IRC server specified.")
        elif not self.relay and not self.idle and not self.password:
            self.logger.warning("IRC plugin loaded, but no channels or password set. Not connecting.")
        else:
            self.irc = SimpleAsyncIrc(self.server, self.nickname, self.password, self.handle_msg, self.handle_perform)
            self.irc.start()
            self.logger.info("Connecting to {}...".format(self.server))

    def handle_chat(self, player, msg, channel):
        if self.irc and self.relay and channel == "chat" and not msg.startswith("!"):
            text = "^7<{}> ^2{}".format(player.name, msg)
            self.irc.msg(self.relay, self.translate_colors(text))

    def handle_unload(self, plugin):
        if plugin == self.__class__.__name__ and self.irc and self.irc.is_alive():
            self.irc.quit("Plugin unloaded!")
            self.irc.stop()


    def handle_msg(self, irc, user, channel, msg):
        if not msg:
            return
        msg_text = " ".join(msg)
        cmd = msg[0].lower()
        if channel.lower() == self.relay.lower():
            if cmd == ("!server"):
                self.server_report(self.relay)
            elif self.is_relaying:
                if not msg_text.startswith("!"):
                    minqlx.SPECTATOR_CHAT_CHANNEL.reply("[TWITCH] ^6{}^7:^2 {}".format(user[0], " ".join(msg)))
                    if "cyardor" in msg_text and random.choice([False, False, True]):
                        self.irc.msg(channel, "To those that are new to the server. My name is Cyardor and I have been playing Quake for close to 1000 years. (c) Cyardor")
                    elif "burtically" in msg_text and random.choice([False, False, True]):
                        self.irc.msg(channel, "Thank you id Software for the freedom you give to all of us (and for fighting communism) (c) burtically")
            else:
                print("I hope this is the part where we have the handle chat error. twitch.py - line 86")
    def handle_perform(self, irc):
        self.logger.info("Connected to IRC!".format(self.server))

        if self.relay:
            irc.join(self.relay)


    @classmethod
    def translate_colors(cls, text):
        if not cls.get_cvar("qlx_ircColors", bool):
            return cls.clean_text(text)

        for i, color in enumerate(COLORS):
            text = text.replace("^{}".format(i), color)

        return text

    @minqlx.next_frame
    def server_report(self, channel):
        teams = self.teams()
        players = teams["free"] + teams["red"] + teams["blue"] + teams["spectator"]
        game = self.game
        # Make a list of players.
        plist = []
        for t in teams:
            if not teams[t]:
                continue
            elif t == "free":
                plist.append("Free: " + ", ".join([p.clean_name for p in teams["free"]]))
            elif t == "red":
                plist.append("\x0304Red\x03: " + ", ".join([p.clean_name for p in teams["red"]]))
            elif t == "blue":
                plist.append("\x0302Blue\x03: " + ", ".join([p.clean_name for p in teams["blue"]]))
            elif t == "spectator":
                plist.append("\x02Spec\x02: " + ", ".join([p.clean_name for p in teams["spectator"]]))


        # Info about the game state.
        if game.state == "in_progress":
            if game.type_short == "race" or game.type_short == "ffa":
                ginfo = "The game is in progress"
            else:
                ginfo = "The score is \x02\x0304{}\x03 - \x0302{}\x03\x02".format(game.red_score, game.blue_score)
        elif game.state == "countdown":
            ginfo = "The game is about to start"
        else:
            ginfo = "The game is in warmup"

        self.irc.msg(channel, "{} on \x02{}\x02 ({}) with \x02{}/{}\x02 players:" .format(ginfo, self.clean_text(game.map_title),
            game.type_short.upper(), len(players), self.get_cvar("sv_maxClients")))
        self.irc.msg(channel, "{}".format(" ".join(plist)))

# ====================================================================
#                     DUMMY PLAYER & IRC CHANNEL
# ====================================================================

class IrcChannel(minqlx.AbstractChannel):
    name = "irc"
    def __init__(self, irc, recipient):
        self.irc = irc
        self.recipient = recipient

    def __repr__(self):
        return "{} {}".format(str(self), self.recipient)

    def reply(self, msg):
        for line in msg.split("\n"):
            self.irc.msg(self.recipient, irc.translate_colors(line))

class IrcDummyPlayer(minqlx.AbstractDummyPlayer):
    def __init__(self, irc, user):
        self.irc = irc
        self.user = user
        super().__init__(name="IRC-{}".format(irc.nickname))

    @property
    def steam_id(self):
        return minqlx.owner()

    @property
    def channel(self):
        return IrcChannel(self.irc, self.user)

    def tell(self, msg):
        for line in msg.split("\n"):
            self.irc.msg(self.user, irc.translate_colors(line))

# ====================================================================
#                        SIMPLE ASYNC IRC
# ====================================================================

re_msg = re.compile(r"^:([^ ]+) PRIVMSG ([^ ]+) :(.*)$")
re_user = re.compile(r"^(.+)!(.+)@(.+)$")

class SimpleAsyncIrc(threading.Thread):
    def __init__(self, address, nickname, ircPassword, msg_handler, perform_handler, stop_event=threading.Event()):
        split_addr = address.split(":")
        self.host = split_addr[0]
        self.port = int(split_addr[1]) if len(split_addr) > 1 else 6667
        self.nickname = nickname
        self.ircPassword = ircPassword
        self.msg_handler = msg_handler
        self.perform_handler = perform_handler

        self.stop_event = stop_event
        self.reader = None
        self.writer = None
        self.server_options = {}
        super().__init__()

        self._lock = threading.Lock()
        self._old_nickname = self.nickname

    def run(self):
        loop = asyncio.new_event_loop()
        logger = minqlx.get_logger("irc")
        asyncio.set_event_loop(loop)
        while not self.stop_event.is_set():
            try:
                loop.run_until_complete(self.connect())
            except Exception:
                minqlx.log_exception()

            # Disconnected. Try reconnecting in 30 seconds.
            logger.info("Disconnected from IRC. Reconnecting in 30 seconds...")
            time.sleep(30)
        loop.close()

    def stop(self):
        self.stop_event.set()

    def write(self, msg):
        if self.writer:
            with self._lock:
                self.writer.write(msg.encode(errors="ignore"))

    @asyncio.coroutine
    def connect(self):
        self.reader, self.writer = yield from asyncio.open_connection(self.host, self.port)
        self.write("CAP REQ :twitch.tv/commands\r\nPASS {}\r\nNICK {}\r\n".format(self.ircPassword, self.nickname))

        while not self.stop_event.is_set():
            line = yield from self.reader.readline()
            if not line:
                break
            line = line.decode("utf-8", errors="ignore").rstrip()
            if line:
                yield from self.parse_data(line)

        self.write("QUIT Quit by user.\r\n")
        self.writer.close()

    @asyncio.coroutine
    def parse_data(self, msg):
        split_msg = msg.split()
        if len(split_msg) > 1 and split_msg[0] == "PING":
            self.pong(split_msg[1].lstrip(":"))
        elif len(split_msg) > 3 and split_msg[1] == "PRIVMSG":
            r = re_msg.match(msg)
            user = re_user.match(r.group(1)).groups()
            channel = user[0] if self.nickname == r.group(2) else r.group(2)
            self.msg_handler(self, user, channel, r.group(3).split())
        elif len(split_msg) > 2 and split_msg[1] == "NICK":
            user = re_user.match(split_msg[0][1:])
            if user and user.group(1) == self.nickname:
                self.nickname = split_msg[2][1:]
        elif split_msg[1] == "005":
            for option in split_msg[3:-1]:
                opt_pair = option.split("=", 1)
                if len(opt_pair) == 1:
                    self.server_options[opt_pair[0]] = ""
                else:
                    self.server_options[opt_pair[0]] = opt_pair[1]
        elif len(split_msg) > 1 and split_msg[1] == "433":
            self.nickname = self._old_nickname
        # Stuff to do after we get the MOTD.
        elif re.match(r":[^ ]+ (376|422) .+", msg):
            self.perform_handler(self)


    def msg(self, recipient, msg):
        self.write("PRIVMSG {} :{}\r\n".format(recipient, msg))

    def nick(self, nick):
        with self._lock:
            self._old_nickname = self.nickname
            self.nickname = nick
        self.write("NICK {}\r\n".format(nick))

    def join(self, channels):
        self.write("JOIN {}\r\n".format(channels))

    def pong(self, n):
        self.write("PONG :{}\r\n".format(n))
    def quit(self, reason):
        self.write("QUIT :{}\r\n".format(reason))