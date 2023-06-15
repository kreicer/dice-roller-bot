import topgg
from discord.ext import commands
from functions.workhorses import logger
from functions.config import topgg_enable, topgg_token, log_file


# top.gg integration cog
class Integrations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.dbl_token = topgg_token
        # self.discord_webhook = ""  # Set this to a discord webhook url
        if topgg_enable is True:
            self.bot.topggpy = topgg.DBLClient(bot, topgg_token, autopost=True, post_shard_count=True)
        # self.bot.topgg_webhook = topgg.WebhookManager(bot).dbl_webhook("/dblwebhook", "Password")
        # self.bot.topgg_webhook.run(5000)

    @commands.Cog.listener()
    async def on_autopost_success(self):
        log_txt = f"Posted stats on Top.gg successful"
        logger(log_file, "INFO", log_txt)

    @commands.Cog.listener()
    async def on_autopost_error(self):
        log_txt = f"Could not post stats on Top.gg"
        logger(log_file, "ERROR", log_txt)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Integrations(bot))
