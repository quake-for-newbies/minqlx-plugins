# Quake For Newbies minqlx plugins

[Minqlx](https://github.com/MinoMino/minqlx) plugins used on the Quake For Newbies Quake Live servers.

* `antihoag.py`, by rinrekku - when a player reaches a max winstreak of 3, they get moved to spectators.
* `disable_ca.py`, by burtically - disable votemap to the clan arena game mode.
* `twitch.py`, by tumer - a light fork of [irc.py](https://github.com/MinoMino/minqlx-plugins/blob/master/irc.py), bridges twitch chat and quake live chat. Twitch chat receives all chat, while in game only spectators receive twitch chat messages.
* `discord_commands.py`, by tumer - a light fork of [discordbot.py](https://github.com/MinoMino/minqlx-plugins/blob/master/discordbot.py), handles !commands from in game chat to discord channels. To be completed with more !commands, only !promote for now.
	* `qlx_discord_role_id = region role`
	* `qlx_discord_lfg_channel_id = discord channel to send messages to`
	* `qlx_discord_bot_token = your bot token`
