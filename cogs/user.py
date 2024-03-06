import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from functions.colorizer import Colorizer
from functions.sql import select_sql, select_all_sql
from lang.EN.errors import sql_operational_error, cmd_on_cooldown
from models.commands import cmds
from models.metrics import commands_counter, errors_counter
from functions.generators import generate_me_output
from functions.config import dev_link, db_user
from models.sql.common import stat_get_dice, shortcut_count, custom_dice_count
from models.sql.user import autocomplete_get_all
from ui.user import StatView


# USER COG
class My(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # USER COMMANDS
    @app_commands.command(name=cmds["me"]["name"], description=cmds["me"]["brief"],)
    @app_commands.checks.cooldown(2, 1)
    async def _user(self, interaction: discord.Interaction) -> None:
        # main
        dice_stat, shortcut_number, custom_dice_number = "", "", ""
        discord_id = str(interaction.user.id)
        secure = (discord_id,)
        try:
            dice_stat = select_sql(db_user, stat_get_dice, secure)
            shortcut_number = select_sql(db_user, shortcut_count, secure)
            custom_dice_number = select_sql(db_user, custom_dice_count, secure)
        except sqlite3.OperationalError:
            errors_counter.labels("me", "OperationalError")
            errors_counter.labels("me", "OperationalError").inc()
            text = Colorizer(sql_operational_error.format(dev_link)).colorize()
            await interaction.response.send_message(content=text, ephemeral=True)
        if dice_stat == "":
            dice_stat = 0
        if shortcut_number == "":
            shortcut_number = 0
        if custom_dice_number == "":
            custom_dice_number = 0
        raw_auto = select_all_sql(db_user, autocomplete_get_all, secure)
        if raw_auto:
            auto = [d[0] for d in raw_auto]
        else:
            auto = []
        view = StatView()
        result = generate_me_output(discord_id, dice_stat, shortcut_number, custom_dice_number, auto)

        # metrics
        commands_counter.labels("me")
        commands_counter.labels("me").inc()

        # answer
        await interaction.response.send_message(content=result, ephemeral=True, view=view)

    # PREFIX ERRORS HANDLER
    @_user.error
    async def on_application_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            errors_counter.labels("me", "CommandOnCooldown")
            errors_counter.labels("me", "CommandOnCooldown").inc()
            retry = round(error.retry_after, 2)
            text = Colorizer(cmd_on_cooldown.format(retry)).colorize()
            await interaction.response.send_message(content=text, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(My(bot))
