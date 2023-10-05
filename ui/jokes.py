import random

import discord
from discord.ext import commands

from functions.colorizer import Colorizer
from functions.config import dir_jokes, log_file, db_jokes
from functions.generators import generate_joke_output
from functions.sql import select_sql
from functions.workhorses import text_writer, logger
from lang.EN.buttons import joke_joke_another, joke_joke_submit
from lang.EN.errors import bad_argument
from lang.EN.ui import joke_modal_submit_joke, joke_modal_text_user, joke_modal_text_user_placeholder, \
    joke_modal_text_joke, joke_modal_text_joke_placeholder, joke_modal_submit_message
from models.metrics import ui_counter, ui_errors_counter
from models.sql import joke_get


# JOKE UI
class JokesView(discord.ui.View):
    def __init__(self, number_of_jokes: int, timeout=None):
        self.number_of_jokes = number_of_jokes
        super().__init__(timeout=timeout)

    @discord.ui.button(label=joke_joke_another, style=discord.ButtonStyle.blurple, emoji="😜")
    async def _another_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # main
        random_joke_number = random.randint(1, self.number_of_jokes)
        joke_id = random_joke_number
        secure = (joke_id,)
        joke_text = select_sql(db_jokes, joke_get, secure)

        # metrics
        ui_counter.labels("button", "joke")
        ui_counter.labels("button", "joke").inc()

        # answer
        result = generate_joke_output(joke_id, joke_text)
        await interaction.response.edit_message(content=result)

    @discord.ui.button(label=joke_joke_submit, style=discord.ButtonStyle.blurple, emoji="📝")
    async def _submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # metrics
        ui_counter.labels("button", "joke")
        ui_counter.labels("button", "joke").inc()

        # answer
        modal = SubmitJoke()
        await interaction.response.send_modal(modal)


class SubmitJoke(discord.ui.Modal, title=joke_modal_submit_joke):
    username = discord.ui.TextInput(
        label=joke_modal_text_user,
        style=discord.TextStyle.short,
        placeholder=joke_modal_text_user_placeholder,
        required=True,
        min_length=3,
        max_length=30,
        row=1
    )

    joke_text = discord.ui.TextInput(
        label=joke_modal_text_joke,
        style=discord.TextStyle.long,
        placeholder=joke_modal_text_joke_placeholder,
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
        ui_counter.labels("modal", "joke")
        ui_counter.labels("modal", "joke").inc()

        # answer
        await interaction.response.send_message(joke_modal_submit_message, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, commands.BadArgument):
            ui_errors_counter.labels("modal", "joke", "BadArgument")
            ui_errors_counter.labels("modal", "joke", "BadArgument").inc()
            error_text = error.args[0]
            text = Colorizer(bad_argument.format(error_text)).colorize()
            await interaction.response.send_message(text, ephemeral=True)



