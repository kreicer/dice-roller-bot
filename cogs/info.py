from discord.ext import commands


# user cog
class Info(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Info(bot))
