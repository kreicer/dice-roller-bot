import sqlite3
from discord.ext import commands

from functions.colorizer import Colorizer
from functions.sql import select_sql, select_all_sql
from lang.EN.errors import bot_missing_permissions, missing_permissions, sql_operational_error
from lang.EN.texts import command_prefix_output_cur
from models.limits import shortcuts_limit
from models.commands import cmds
from models.metrics import commands_counter, errors_counter
from functions.generators import generate_prefix_output, generate_shortcut_output, \
    generate_shortcut_empty_output
from functions.config import db_admin, dev_link, bot_prefix
from models.sql import prefix_get, shortcut_get_all, shortcut_count
from ui.server import PrefixView, ShortcutView


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
        view = PrefixView(author=ctx.author)
        result = generate_prefix_output(guild_prefix, command_prefix_output_cur)

        # metrics
        commands_counter.labels("prefix")
        commands_counter.labels("prefix").inc()

        # answer
        await ctx.defer(ephemeral=True)
        view.message = await ctx.send(result, view=view)

    # SHORTCUT COMMANDS GROUP
    @commands.hybrid_command(name=cmds["shortcut"]["name"], brief=cmds["shortcut"]["brief"],
                             aliases=cmds["shortcut"]["aliases"], with_app_command=True)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _shortcut(self, ctx: commands.Context) -> None:
        # main
        discord_id = str(ctx.guild.id)
        secure = (discord_id,)
        shortcuts = select_all_sql(db_admin, shortcut_get_all, secure)
        view = ShortcutView(author=ctx.author, discord_id=discord_id)
        if shortcuts:
            shortcut_number = select_sql(db_admin, shortcut_count, secure)
            result = generate_shortcut_output(shortcuts, shortcut_number, shortcuts_limit)
        else:
            result = generate_shortcut_empty_output()

        # metrics
        commands_counter.labels("shortcut")
        commands_counter.labels("shortcut").inc()

        # answer
        await ctx.defer(ephemeral=True)
        view.message = await ctx.send(result, view=view)

    # PREFIX ERRORS HANDLER
    @_prefix.error
    async def _prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            errors_counter.labels("prefix", "MissingPermissions")
            errors_counter.labels("prefix", "MissingPermissions").inc()
            text = Colorizer(missing_permissions).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        if isinstance(error, sqlite3.OperationalError):
            errors_counter.labels("prefix", "OperationalError")
            errors_counter.labels("prefix", "OperationalError").inc()
            text = Colorizer(sql_operational_error.format(dev_link)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("prefix", "BotMissingPermissions")
            errors_counter.labels("prefix", "BotMissingPermissions").inc()
            text = Colorizer(bot_missing_permissions).colorize()
            dm = await ctx.author.create_dm()
            await dm.send(text)

    # SHORTCUT ERRORS HANDLER
    @_shortcut.error
    async def _shortcut_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            errors_counter.labels("shortcut_add", "MissingPermissions")
            errors_counter.labels("shortcut_add", "MissingPermissions").inc()
            text = Colorizer(missing_permissions).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        if isinstance(error, sqlite3.OperationalError):
            errors_counter.labels("prefix", "OperationalError")
            errors_counter.labels("prefix", "OperationalError").inc()
            text = Colorizer(sql_operational_error.format(dev_link)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("shortcut", "BotMissingPermissions")
            errors_counter.labels("shortcut", "BotMissingPermissions").inc()
            text = Colorizer(bot_missing_permissions).colorize()
            dm = await ctx.author.create_dm()
            await dm.send(text)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Server(bot))
