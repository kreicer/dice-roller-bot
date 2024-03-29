import traceback

from discord.ext import commands, tasks

from functions.colorizer import Colorizer
from functions.logging import log_info, log_error
from functions.generators import generate_info_output, generate_help_short_output
from lang.EN.errors import bot_missing_permissions, cmd_on_cooldown
from lang.EN.texts import command_hello_text
from models.commands import cmds, cogs
from models.metrics import commands_counter, errors_counter
from ui.community import HelpView, AboutView

guilds_number = 0


# COMMUNITY COG
class Community(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self._update_servers_number.start()

    def cog_unload(self):
        self._update_servers_number.cancel()

    @tasks.loop(hours=1)
    async def _update_servers_number(self):
        global guilds_number
        guilds_number = len(self.bot.guilds)
        # Logger
        log_txt = "Guild number updated, current number: " + str(guilds_number)
        log_info(log_txt)

    @_update_servers_number.before_loop
    async def _before_update_servers_number(self):
        await self.bot.wait_until_ready()

    # HELP COMMAND
    @commands.hybrid_command(name=cmds["hlp"]["name"], brief=cmds["hlp"]["brief"], aliases=cmds["hlp"]["aliases"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 1, commands.BucketType.user)
    async def _help(self, ctx: commands.Context) -> None:
        result = generate_help_short_output(cogs)
        view = HelpView()

        commands_counter.labels("help")
        commands_counter.labels("help").inc()

        await ctx.defer(ephemeral=True)
        await ctx.send(result, view=view)

    # ABOUT COMMAND
    @commands.hybrid_command(name=cmds["about"]["name"], brief=cmds["about"]["brief"], aliases=cmds["about"]["aliases"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 1, commands.BucketType.user)
    async def _about(self, ctx: commands.Context) -> None:
        result = generate_info_output(guilds_number)
        view = AboutView()

        commands_counter.labels("about")
        commands_counter.labels("about").inc()
        await ctx.defer(ephemeral=True)
        await ctx.send(result, view=view)

    # HELLO COMMAND
    @commands.hybrid_command(name=cmds["hello"]["name"], brief=cmds["hello"]["brief"], aliases=cmds["hello"]["aliases"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 1, commands.BucketType.user)
    async def _hello(self, ctx: commands.Context) -> None:
        output = Colorizer(command_hello_text).colorize()

        commands_counter.labels("hello")
        commands_counter.labels("hello").inc()

        await ctx.defer(ephemeral=True)
        await ctx.send(output)

    # ABOUT ERRORS HANDLER
    @_about.error
    async def _about_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("about", "BotMissingPermissions")
            errors_counter.labels("about", "BotMissingPermissions").inc()
            text = Colorizer(bot_missing_permissions).colorize()
            dm = await ctx.author.create_dm()
            await dm.send(text)
        elif isinstance(error, commands.CommandOnCooldown):
            errors_counter.labels("roll", "CommandOnCooldown")
            errors_counter.labels("roll", "CommandOnCooldown").inc()
            retry = round(error.retry_after, 2)
            text = Colorizer(cmd_on_cooldown.format(retry)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        else:
            traceback.print_exception(type(error), error, error.__traceback__)
            text = type(error) + error + error.__traceback__
            log_error(text)

    # HELP ERRORS HANDLER
    @_help.error
    async def _help_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("about", "BotMissingPermissions")
            errors_counter.labels("about", "BotMissingPermissions").inc()
            text = Colorizer(bot_missing_permissions).colorize()
            dm = await ctx.author.create_dm()
            await dm.send(text)
        elif isinstance(error, commands.CommandOnCooldown):
            errors_counter.labels("roll", "CommandOnCooldown")
            errors_counter.labels("roll", "CommandOnCooldown").inc()
            retry = round(error.retry_after, 2)
            text = Colorizer(cmd_on_cooldown.format(retry)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        else:
            traceback.print_exception(type(error), error, error.__traceback__)
            text = type(error) + error + error.__traceback__
            log_error(text)

    # HELLO ERRORS HANDLER
    @_hello.error
    async def _hello_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("hello", "BotMissingPermissions")
            errors_counter.labels("hello", "BotMissingPermissions").inc()
            text = Colorizer(bot_missing_permissions).colorize()
            dm = await ctx.author.create_dm()
            await dm.send(text)
        elif isinstance(error, commands.CommandOnCooldown):
            errors_counter.labels("roll", "CommandOnCooldown")
            errors_counter.labels("roll", "CommandOnCooldown").inc()
            retry = round(error.retry_after, 2)
            text = Colorizer(cmd_on_cooldown.format(retry)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        else:
            traceback.print_exception(type(error), error, error.__traceback__)
            text = type(error) + error + error.__traceback__
            log_error(text)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Community(bot))
