from __future__ import annotations

import logging
from typing import override

import discord
from discord.ext import commands
from discord_logging_handler import UserLogHandler

from . import red_light_commands
from .bot_settings import BotSettings, get_bot_settings


class RedLightBot(commands.Bot):
    def __init__(self):
        self._settings: BotSettings = get_bot_settings()

        self._first_on_ready: bool = True
        self._logger = logging.getLogger(RedLightBot.__name__)
        self._logger.setLevel(logging.DEBUG)

        # setup discord bot
        discord.VoiceClient.warn_dave = False
        discord.VoiceClient.warn_nacl = False
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    def run(self, token: str, *args, **kwargs) -> None:
        super().run(token, *args, **kwargs)

    @override
    async def on_ready(self) -> None:
        self._logger.debug(self._logging_header("on_ready Enter"))

        if self._first_on_ready:
            self._first_on_ready = False

            self._logger.debug("Setting Up commands")
            await red_light_commands.setup(self)
            await self.tree.sync()

            self._logger.debug("Setting up discord logger")
            discord_handler = UserLogHandler(self, self._settings.dev)
            discord_handler.setLevel(logging.INFO)
            logging.getLogger().addHandler(discord_handler)

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="The light"
            )
        )
        self._logger.debug(self._logging_header("on_ready Exit"))
        self._logger.info("Bot Started")

    def _logging_header(self, message: str) -> str:
        target_length = 40

        dash_count = (target_length - len(message)) // 2
        return "-" * dash_count + message + "-" * dash_count

    async def shutdown(self):
        self._logger.debug(f"Shutting down {RedLightBot.__name__}")

        await self.close()
