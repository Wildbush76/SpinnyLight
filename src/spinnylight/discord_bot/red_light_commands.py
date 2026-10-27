from __future__ import annotations

from logging import getLogger
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from ..client.light_client import get_light_client
from .bot_settings import get_bot_settings


class ShreddedCabbageCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot
        self._logger = getLogger(ShreddedCabbageCommands.__name__)
        self._settings = get_bot_settings()
        self._red_light_client = get_light_client()

    async def _send_file(
        self, interaction: discord.Interaction, file: Path, message: str | None = None
    ):
        if not file.exists():
            await interaction.response.send_message(f"File: {file.name} not found!")
            self._logger.warning(f"Send-File: Failed to file file: {file.name}")
            return
        file = discord.File(file)
        await interaction.response.send_message(content=message, file=file)

    @app_commands.command(name="log_dump")
    async def _log_dump(self, interaction: discord.Interaction):
        self._logger.debug("Dumping logs")
        await self._send_file(interaction, self._settings.log_file, "Log file")

    @app_commands.command(name="clear_logs")
    async def _clear_logs(self, interaction: discord.Interaction):
        if self._settings.log_file.exists():
            self._settings.log_file.unlink()
            await interaction.response.send_message(content="Logs cleared")
        else:
            await interaction.response.send_message("No logs found")
        self._logger.debug("Clearing logs")

    @app_commands.command(name="trigger_light")
    async def _trigger_light(self, interaction: discord.Interaction):
        self._red_light_client.trigger()
        await interaction.response.send_message("Trigger the light! C:")


async def setup(bot: commands.Bot):
    await bot.add_cog(ShreddedCabbageCommands(bot))
