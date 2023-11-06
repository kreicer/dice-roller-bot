import discord
from discord.ext import commands, tasks

from functions.colorizer import Colorizer
from functions.workhorses import logger
from functions.generators import generate_info_output, generate_help_short_output
from functions.config import log_file, community_support, dev_github, topgg_link, community_policy
from lang.EN.buttons import community_help_support, community_about_policy
from lang.EN.errors import bot_missing_permissions
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
        logger(log_file, "INFO", log_txt)

    @_update_servers_number.before_loop
    async def _before_update_servers_number(self):
        await self.bot.wait_until_ready()

    # HELP COMMAND
    @commands.hybrid_command(name=cmds["hlp"]["name"], brief=cmds["hlp"]["brief"], aliases=cmds["hlp"]["aliases"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _help(self, ctx: commands.Context) -> None:
        result = generate_help_short_output(cogs)

        view = HelpView()
        view.add_item(discord.ui.Button(label=community_help_support, style=discord.ButtonStyle.link,
                                        url=community_support, emoji="🆘", row=2))

        commands_counter.labels("help")
        commands_counter.labels("help").inc()

        await ctx.defer(ephemeral=True)
        view.message = await ctx.send(result, view=view)

    # ABOUT COMMAND
    @commands.hybrid_command(name=cmds["about"]["name"], brief=cmds["about"]["brief"], aliases=cmds["about"]["aliases"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _about(self, ctx: commands.Context) -> None:

        result = generate_info_output(guilds_number)

        view = AboutView()
        view.add_item(discord.ui.Button(label="Github", style=discord.ButtonStyle.link,
                                        url=dev_github, emoji="🧑‍💻"))
        view.add_item(discord.ui.Button(label="Top.gg", style=discord.ButtonStyle.link,
                                        url=topgg_link, emoji="👍"))
        view.add_item(discord.ui.Button(label=community_about_policy, style=discord.ButtonStyle.link,
                                        url=community_policy, emoji="🔏"))

        commands_counter.labels("about")
        commands_counter.labels("about").inc()
        await ctx.defer(ephemeral=True)
        await ctx.send(result, view=view)

    # HELLO COMMAND
    @commands.hybrid_command(name=cmds["hello"]["name"], brief=cmds["hello"]["brief"], aliases=cmds["hello"]["aliases"],
                             with_app_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
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

    # HELP ERRORS HANDLER
    @_help.error
    async def _help_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("about", "BotMissingPermissions")
            errors_counter.labels("about", "BotMissingPermissions").inc()
            text = Colorizer(bot_missing_permissions).colorize()
            dm = await ctx.author.create_dm()
            await dm.send(text)

    # HELLO ERRORS HANDLER
    @_hello.error
    async def _hello_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("hello", "BotMissingPermissions")
            errors_counter.labels("hello", "BotMissingPermissions").inc()
            text = Colorizer(bot_missing_permissions).colorize()
            dm = await ctx.author.create_dm()
            await dm.send(text)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Community(bot))
