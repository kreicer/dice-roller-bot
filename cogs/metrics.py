from discord.ext import commands, tasks
from prometheus_client import start_http_server
from functions.config import metrics_port, metrics_enable


# METRICS COG
class Metrics(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        if metrics_enable is True:
            self._start_web_server.start()

    def cog_unload(self):
        self._start_web_server.cancel()

    @tasks.loop(count=1)
    async def _start_web_server(self):
        start_http_server(metrics_port)

    @_start_web_server.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Metrics(bot))
