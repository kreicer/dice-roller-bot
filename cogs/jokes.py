import sqlite3
import random

import discord
from discord.ext import commands, tasks

from classes.ui import Feedback
from functions.sql import select_sql
from models.commands import cmds
from functions.workhorses import text_writer, logger, generate_joke_output
from functions.config import db_jokes, dir_jokes, log_file
from models.metrics import commands_counter, errors_counter, ui_modals_counter, ui_button_counter
from models.sql import joke_get, jokes_count

# global
number_of_jokes = 1


# JOKES UI
class SubmitJoke(Feedback, title="Submit joke"):
    joke_text = discord.ui.TextInput(
        label="Joke",
        style=discord.TextStyle.long,
        placeholder="Write your joke text here...",
        required=True,
        min_length=10,
        max_length=3000,
        row=2
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # main
        username = self.username.value
        joke_text = self.joke_text.value
        text = f"username: \"{username}\"\n" \
               f"joke: \"{joke_text}\"\n"
        text_writer(text, dir_jokes)

        # logger
        log_txt = f"[ joke -> button 'submit joke' ] New joke was posted by {username}"
        logger(log_file, "INFO", log_txt)

        # metrics
        ui_modals_counter.labels("joke", "submit")
        ui_modals_counter.labels("joke", "submit").inc()

        # answer
        await interaction.response.send_message("Thanks for your joke!", ephemeral=True)


class JokesView(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Another joke", style=discord.ButtonStyle.blurple, emoji="😜")
    async def _another_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # main
        random_joke_number = random.randint(1, number_of_jokes)
        joke_id = random_joke_number
        secure = (joke_id,)
        joke_text = select_sql(db_jokes, joke_get, secure)

        # metrics
        ui_button_counter.labels("joke", "another")
        ui_button_counter.labels("joke", "another").inc()

        # answer
        result = generate_joke_output(joke_id, joke_text)
        await interaction.response.edit_message(content=result)

    @discord.ui.button(label="Submit joke", style=discord.ButtonStyle.blurple, emoji="📝")
    async def _submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # metrics
        ui_button_counter.labels("joke", "submit")
        ui_button_counter.labels("joke", "submit").inc()

        # answer
        modal = SubmitJoke()
        await interaction.response.send_modal(modal)


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
        view.add_item(discord.ui.Button(label="Rate jokes", style=discord.ButtonStyle.link,
                                        url="https://discord.gg/TuXxE57kqy", emoji="🤩"))
        result = generate_joke_output(joke_id, joke_text)
        await ctx.defer(ephemeral=True)
        await ctx.send(result, view=view)

    # JOKE ERRORS HANDLER
    @_joke.error
    async def _joke_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("joke", "BotMissingPermissions")
            errors_counter.labels("joke", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Jokes(bot))
