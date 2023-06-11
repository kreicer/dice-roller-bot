from discord.ext import commands, tasks
from models.commands import stat as st, about as ab
from functions.workhorses import logger
from functions.config import bot_name, bot_version, bot_dev, default_shards, log_file, github, topgg, policy
from models.metrics import commands_used_about, commands_used_stat

guilds_number = 0


# user cog
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

    @commands.hybrid_command(name=st["name"], brief=st["brief"], usage=st["usage"], help=st["help"],
                             with_app_command=True)
    async def _stat(self, ctx: commands.Context) -> None:
        commands_used_stat.inc()

        await ctx.defer(ephemeral=True)
        await ctx.send(f'**STATISTICS**\n'
                       f'Shards: {default_shards}\n'
                       f'Servers: {guilds_number}')

    @commands.hybrid_command(name=ab["name"], brief=ab["brief"], usage=ab["usage"], help=ab["help"],
                             with_app_command=True)
    async def _about(self, ctx: commands.Context) -> None:
        commands_used_about.inc()

        await ctx.defer(ephemeral=True)
        await ctx.send(f'**{bot_name}**\n'
                       f'Developer: {bot_dev}\n'
                       f'Version: {bot_version}\n'
                       f'Github: {github}\n'
                       f'Top.gg: {topgg}\n'
                       f'Privacy Policy: {policy}')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Info(bot))
