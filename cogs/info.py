from discord.ext import commands, tasks
from models.commands import stat as st, about as ab
from functions.workhorses import logger
from functions.config import (bot_name,
                              bot_version,
                              dev_name,
                              bot_shards,
                              log_file,
                              dev_github,
                              topgg_link,
                              community_policy)
from models.metrics import commands_counter, errors_counter

guilds_number = 0


# INFO COG
class Info(commands.Cog):
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
    async def before_printer(self):
        await self.bot.wait_until_ready()

    # STAT COMMAND
    @commands.hybrid_command(name=st["name"], brief=st["brief"], usage=st["usage"], help=st["help"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _stat(self, ctx: commands.Context) -> None:
        commands_counter.labels("stat")
        commands_counter.labels("stat").inc()

        await ctx.defer(ephemeral=True)
        await ctx.send(f'**STATISTICS**\n'
                       f'Shards: {bot_shards}\n'
                       f'Servers: {guilds_number}')

    # ABOUT COMMAND
    @commands.hybrid_command(name=ab["name"], brief=ab["brief"], usage=ab["usage"], help=ab["help"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _about(self, ctx: commands.Context) -> None:
        commands_counter.labels("about")
        commands_counter.labels("about").inc()

        await ctx.defer(ephemeral=True)
        await ctx.send(f'**{bot_name}**\n'
                       f'Developer: {dev_name}\n'
                       f'Version: {bot_version}\n'
                       f'Github: {dev_github}\n'
                       f'Top.gg: {topgg_link}\n'
                       f'Privacy Policy: {community_policy}')

    # STAT ERRORS HANDLER
    @_stat.error
    async def _stat_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("stat", "BotMissingPermissions")
            errors_counter.labels("stat", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')

    # ABOUT ERRORS HANDLER
    @_about.error
    async def _about_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("about", "BotMissingPermissions")
            errors_counter.labels("about", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Info(bot))
