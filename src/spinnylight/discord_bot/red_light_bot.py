from __future__ import annotations

import logging

import discord
from discord.ext import commands
from discord.ext.logging import UserLogHandler, get_user_log_handler

from . import red_light_commands
from .bot_settings import BotSettings, get_bot_settings


class RedLightBot(commands.Bot):
    def __init__(self):
        self._settings: BotSettings = get_bot_settings()

        # Logging
        self._logger = logging.getLogger(RedLightBot.__name__)
        self._logger.setLevel(logging.DEBUG)
        discord_handler: UserLogHandler = get_user_log_handler(self, self._settings.dev)
        discord_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(discord_handler)

        # setup discord bot
        discord.VoiceClient.warn_dave = False
        discord.VoiceClient.warn_nacl = False
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    def run(self, token: str, *args, **kwargs) -> None:
        super().run(token, *args, **kwargs)

    async def setup_hook(self):
        await red_light_commands.setup(self)
        await self.tree.sync()

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="The light"
            )
        )
        self._logger.info("Bot Started")

    def _logging_header(self, message: str) -> str:
        target_length = 40

        dash_count = (target_length - len(message)) // 2
        return "-" * dash_count + message + "-" * dash_count

    async def shutdown(self):
        self._logger.info(f"Shutting down {RedLightBot.__name__}")

        await self.close()
