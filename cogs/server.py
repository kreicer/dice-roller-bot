import sqlite3
import traceback
import typing

import discord
from discord.ext import commands

from functions.sql import apply_sql, select_sql
from models.commands import cmds
from models.metrics import commands_counter, errors_counter, ui_modals_counter, ui_button_counter
from functions.workhorses import logger, generate_prefix_output
from functions.config import db_admin, dev_link, log_file, bot_prefix
from models.sql import source_update, prefix_update, prefix_delete, prefix_get


# SERVER UI
class SetPrefix(discord.ui.Modal, title="Set new prefix"):
    new_prefix = discord.ui.TextInput(
        label="New prefix",
        style=discord.TextStyle.short,
        placeholder="Write server new prefix here...",
        required=True,
        min_length=1,
        max_length=3,
        row=1
    )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        traceback.print_exception(type(error), error, error.__traceback__)
        await interaction.response.send_message("Something went wrong...", ephemeral=True)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # main
        new_prefix = str(self.new_prefix.value)
        discord_id = str(interaction.guild_id)
        source_type = 1
        secure_src = (discord_id, source_type)
        secure_prefix = (discord_id, new_prefix)
        execute_list = [(source_update, secure_src), (prefix_update, secure_prefix)]
        success = apply_sql(db_admin, execute_list)
        if success:
            # logger
            log_txt = f"[ prefix -> button 'set prefix' ] New prefix was set on {discord_id} server"
            logger(log_file, "INFO", log_txt)

            # metrics
            ui_modals_counter.labels("prefix", "set")
            ui_modals_counter.labels("prefix", "set").inc()

            # answer
            result = generate_prefix_output(new_prefix, "New guild prefix value")
            await interaction.response.edit_message(content=result)
        else:
            # logger
            log_txt = f"Failed to load database file - {db_admin}"
            logger(log_file, "ERROR", log_txt)

            # answer
            await interaction.response.send_message(f"**SQL Operational Error**\n"
                                                    f"Looks like Admin Database currently unavailable.\n"
                                                    f"Please, report to [developer]({dev_link}).", ephemeral=True)


class PrefixView(discord.ui.View):
    def __init__(self, author: typing.Union[discord.Member, discord.User], timeout=None):
        self.author = author
        super().__init__(timeout=timeout)

    # check user click vs user spawn
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message(f'**Missing Permissions**\n'
                                                    f'Sorry, but you need administrator permissions to manage prefix '
                                                    f'for this server.', ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Set prefix", style=discord.ButtonStyle.gray, emoji="📥")
    async def _set_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # metrics
        ui_button_counter.labels("prefix", "set")
        ui_button_counter.labels("prefix", "set").inc()

        # answer
        modal = SetPrefix()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Restore prefix", style=discord.ButtonStyle.gray, emoji="📤")
    async def _restore_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # main
        discord_id = str(interaction.guild_id)
        secure = (discord_id,)
        execute_list = [(prefix_delete, secure)]
        success = apply_sql(db_admin, execute_list)
        if success:
            # logger
            log_txt = f"[ prefix -> button 'restore prefix' ] Prefix was restored on {discord_id} server"
            logger(log_file, "INFO", log_txt)

            # metrics
            ui_modals_counter.labels("prefix", "restore")
            ui_modals_counter.labels("prefix", "restore").inc()

            # answer
            result = generate_prefix_output(bot_prefix, "Guild prefix value was restored to default")
            await interaction.response.edit_message(content=result)
        else:
            # logger
            log_txt = f"Failed to load database file - {db_admin}"
            logger(log_file, "ERROR", log_txt)

            # answer
            await interaction.response.send_message(f"**SQL Operational Error**\n"
                                                    f"Looks like Admin Database currently unavailable.\n"
                                                    f"Please, report to [developer]({dev_link}).", ephemeral=True)


# SERVER COG
class Server(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # PREFIX COMMANDS GROUP
    @commands.hybrid_command(name=cmds["prefix"]["name"], brief=cmds["prefix"]["brief"],
                             aliases=cmds["prefix"]["aliases"], with_app_command=True)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _prefix(self, ctx: commands.Context) -> None:
        # main
        discord_id = str(ctx.guild.id)
        secure = (discord_id,)
        guild_prefix = select_sql(db_admin, prefix_get, secure)
        if guild_prefix == "":
            guild_prefix = bot_prefix

        # metrics
        commands_counter.labels("prefix")
        commands_counter.labels("prefix").inc()

        # answer
        view = PrefixView(author=ctx.author)
        result = generate_prefix_output(guild_prefix, "Current guild prefix value")
        await ctx.defer(ephemeral=True)
        await ctx.send(result, view=view)

    # SHORTCUT COMMANDS GROUP
    # @commands.hybrid_group(name=srt["name"], brief=srt["brief"], help=srt["help"], aliases=srt["aliases"],
    #                       invoke_without_command=True, with_app_command=True)
    # @commands.has_permissions(administrator=True)
    # @commands.bot_has_permissions(send_messages=True)
    # async def _shortcut(self, ctx: commands.Context) -> None:
    #    if ctx.invoked_subcommand is None:
    #        prefix = ctx.prefix

    #        commands_counter.labels("shortcut")
    #        commands_counter.labels("shortcut").inc()

    #        await ctx.defer(ephemeral=True)
    #        await ctx.send(f'Please choose: you want to list shortcuts, add it or remove it.'
    #                       f'```{prefix}shortcut list```'
    #                       f'```{prefix}shortcut add```'
    #                       f'```{prefix}shortcut remove```')

    # PREFIX ERRORS HANDLER
    @_prefix.error
    async def _prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            errors_counter.labels("prefix", "MissingPermissions")
            errors_counter.labels("prefix", "MissingPermissions").inc()
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Missing Permissions**\n'
                           f'Sorry, but you need administrator permissions to manage prefix for this server.')
        if isinstance(error, sqlite3.OperationalError):
            errors_counter.labels("prefix", "OperationalError")
            errors_counter.labels("prefix", "OperationalError").inc()
            await ctx.defer(ephemeral=True)
            await ctx.send(f"**SQL Operational Error**\n"
                           f"Looks like Admin Database currently unavailable.\n"
                           f"Please, report to [developer]({dev_link}).")
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("prefix", "BotMissingPermissions")
            errors_counter.labels("prefix", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')

    # SHORTCUT ERRORS HANDLER
    # @_shortcut.error
    # async def _shortcut_error(self, ctx, error):
    #    if isinstance(error, commands.MissingPermissions):
    #        errors_counter.labels("shortcut_add", "MissingPermissions")
    #        errors_counter.labels("shortcut_add", "MissingPermissions").inc()
    #        await ctx.defer(ephemeral=True)
    #        await ctx.send(f'**Missing Permissions**\n'
    #                       f'Sorry, but you need administrator permissions to manage shortcuts for this server.')
    #    if isinstance(error, commands.BotMissingPermissions):
    #        errors_counter.labels("shortcut", "BotMissingPermissions")
    #        errors_counter.labels("shortcut", "BotMissingPermissions").inc()
    #        dm = await ctx.author.create_dm()
    #        await dm.send(f'**Bot Missing Permissions**\n'
    #                      f'Dice Roller have missing permissions to answer you in this channel.\n'
    #                      f'You can solve it by adding rights in channel or server management section.')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Server(bot))
