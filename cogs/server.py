import sqlite3
import traceback

import discord
from discord import app_commands
from discord.ext import commands

from functions.colorizer import Colorizer
from functions.logging import log_error
from functions.sql import select_sql
from lang.EN.errors import missing_permissions, sql_operational_error, cmd_on_cooldown
from models.commands import cmds
from models.metrics import commands_counter, errors_counter
from functions.generators import generate_stat_output
from functions.config import db_admin, dev_link
from models.sql.common import shortcut_count, stat_get_dice, custom_dice_count
from ui.server import StatView


# SERVER COG
class Server(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # CONFIG COMMAND
    @app_commands.command(name=cmds["config"]["name"], description=cmds["config"]["brief"],)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(2, 1)
    async def _config(self, interaction: discord.Interaction) -> None:
        # main
        dice_stat, shortcut_number, custom_dice_number = "", "", ""
        discord_id = str(interaction.guild_id)
        secure = (discord_id,)
        try:
            dice_stat = select_sql(db_admin, stat_get_dice, secure)
            shortcut_number = select_sql(db_admin, shortcut_count, secure)
            custom_dice_number = select_sql(db_admin, custom_dice_count, secure)
        except sqlite3.OperationalError:
            errors_counter.labels("config", "OperationalError")
            errors_counter.labels("config", "OperationalError").inc()
            text = Colorizer(sql_operational_error.format(dev_link)).colorize()
            await interaction.response.send_message(content=text, ephemeral=True)
        if dice_stat == "":
            dice_stat = 0
        if shortcut_number == "":
            shortcut_number = 0
        if custom_dice_number == "":
            custom_dice_number = 0
        view = StatView()
        result = generate_stat_output(discord_id, dice_stat, shortcut_number, custom_dice_number)

        # metrics
        commands_counter.labels("config")
        commands_counter.labels("config").inc()

        # answer
        await interaction.response.send_message(content=result, view=view, ephemeral=True)

    # PREFIX ERRORS HANDLER
    @_config.error
    async def on_application_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            errors_counter.labels("config", "MissingPermissions")
            errors_counter.labels("config", "MissingPermissions").inc()
            text = Colorizer(missing_permissions).colorize()
            await interaction.response.send_message(content=text, ephemeral=True)
        elif isinstance(error, app_commands.CommandOnCooldown):
            errors_counter.labels("config", "CommandOnCooldown")
            errors_counter.labels("config", "CommandOnCooldown").inc()
            retry = round(error.retry_after, 2)
            text = Colorizer(cmd_on_cooldown.format(retry)).colorize()
            await interaction.response.send_message(content=text, ephemeral=True)
        else:
            traceback.print_exception(type(error), error, error.__traceback__)
            text = type(error) + error + error.__traceback__
            log_error(text)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Server(bot))
