import sqlite3
import random

import discord
from discord.ext import commands, tasks

from functions.colorizer import Colorizer
from functions.sql import select_sql
from lang.EN.buttons import joke_joke_rate
from lang.EN.errors import bot_missing_permissions, cmd_on_cooldown
from models.commands import cmds
from functions.workhorses import logger
from functions.generators import generate_joke_output
from functions.config import db_jokes, log_file
from models.metrics import commands_counter, errors_counter
from models.sql.jokes import joke_get, jokes_count
from ui.jokes import JokesView

# global
number_of_jokes = 1


# JOKES COG
class Jokes(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self._update_jokes.add_exception_type(sqlite3.OperationalError)
        self._update_jokes.start()

    def cog_unload(self):
        self._update_jokes.cancel()

    @tasks.loop(hours=1)
    async def _update_jokes(self):
        # main
        global number_of_jokes
        secure = ()
        number_of_jokes = select_sql(db_jokes, jokes_count, secure)

        # logger
        log_txt = "Jokes number updated, current number: " + str(number_of_jokes)
        logger(log_file, "INFO", log_txt)

        # answer
        return number_of_jokes

    @_update_jokes.before_loop
    async def _before_update_jokes(self):
        await self.bot.wait_until_ready()

    # JOKE COMMANDS GROUP
    @commands.hybrid_command(name=cmds["joke"]["name"], brief=cmds["joke"]["brief"], aliases=cmds["joke"]["aliases"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 1, commands.BucketType.user)
    async def _joke(self, ctx: commands.Context) -> None:
        # main
        random_joke_number = random.randint(1, number_of_jokes)
        joke_id = random_joke_number
        secure = (joke_id,)
        joke_text = select_sql(db_jokes, joke_get, secure)

        # metrics
        commands_counter.labels("joke")
        commands_counter.labels("joke").inc()

        # answer
        view = JokesView()
        view.add_item(discord.ui.Button(label=joke_joke_rate, style=discord.ButtonStyle.link,
                                        url="https://discord.gg/TuXxE57kqy", emoji="🤩", row=1))
        result = generate_joke_output(joke_id, joke_text)
        await ctx.defer(ephemeral=True)
        view.message = await ctx.send(result, view=view)

    # JOKE ERRORS HANDLER
    @_joke.error
    async def _joke_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("joke", "BotMissingPermissions")
            errors_counter.labels("joke", "BotMissingPermissions").inc()
            text = Colorizer(bot_missing_permissions).colorize()
            dm = await ctx.author.create_dm()
            await dm.send(text)
        if isinstance(error, commands.CommandOnCooldown):
            errors_counter.labels("roll", "CommandOnCooldown")
            errors_counter.labels("roll", "CommandOnCooldown").inc()
            retry = round(error.retry_after, 2)
            text = Colorizer(cmd_on_cooldown.format(retry)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Jokes(bot))
