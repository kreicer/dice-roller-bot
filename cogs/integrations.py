import topgg
from discord.ext import commands

from functions.logging import log_info, log_error
from functions.config import topgg_enable, topgg_token, topgg_timer
from models.metrics import errors_counter


# TOP.GG INTEGRATION COG
class Integrations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if topgg_enable is True:
            self.bot.topggpy = topgg.DBLClient(bot, topgg_token,
                                               autopost=True, post_shard_count=True, autopost_interval=topgg_timer)

    @commands.Cog.listener()
    async def on_autopost_success(self):
        log_txt = f"Posted stats on Top.gg successful"
        log_info(log_txt)

    @commands.Cog.listener()
    async def on_autopost_error(self, error):
        log_txt = f"Could not post stats on Top.gg: "
        log_txt = log_txt + error
        log_error(log_txt)
        errors_counter.labels("integration", "Exception")
        errors_counter.labels("integration", "Exception").inc()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Integrations(bot))
