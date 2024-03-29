import random
# import traceback

import discord
from discord.ext import commands

from functions.colorizer import Colorizer
from functions.config import dir_jokes, db_jokes
from functions.generators import generate_joke_output
from functions.logging import log_info
from functions.sql import select_sql
from functions.workhorses import text_writer
from lang.EN.buttons import joke_joke_another, joke_joke_submit
from lang.EN.errors import bad_argument
from lang.EN.ui import joke_modal_submit_joke, \
    joke_modal_text_joke, joke_modal_text_joke_placeholder, joke_modal_submit_message
from models.metrics import ui_counter, ui_errors_counter
from models.sql.jokes import joke_get, jokes_count


# JOKE UI
class JokesView(discord.ui.View):
    def __init__(self, timeout=None):
        self.message = None
        super().__init__(timeout=timeout)

    # async def on_timeout(self) -> None:
    #    await self.message.edit(view=None)
    # async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Button) -> None:
    #    traceback.print_exception(type(error), error, error.__traceback__)

    @discord.ui.button(label=joke_joke_another, style=discord.ButtonStyle.gray,
                       emoji="😜", row=1, custom_id="dr_joke_button_another")
    async def _another_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # main
        number_of_jokes = select_sql(db_jokes, jokes_count, ())
        random_joke_number = random.randint(1, number_of_jokes)
        joke_id = random_joke_number
        secure = (joke_id,)
        joke_text = select_sql(db_jokes, joke_get, secure)

        # metrics
        ui_counter.labels("button", "joke", "another")
        ui_counter.labels("button", "joke", "another").inc()

        # answer
        result = generate_joke_output(joke_id, joke_text)
        await interaction.response.edit_message(content=result)

    @discord.ui.button(label=joke_joke_submit, style=discord.ButtonStyle.gray,
                       emoji="📝", row=1, custom_id="dr_joke_button_submit")
    async def _submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # metrics
        ui_counter.labels("button", "joke", "submit")
        ui_counter.labels("button", "joke", "submit").inc()

        # answer
        modal = SubmitJoke()
        await interaction.response.send_modal(modal)


class SubmitJoke(discord.ui.Modal, title=joke_modal_submit_joke):
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
        user_id = interaction.user.id
        joke_text = self.joke_text.value
        text = f"username: \"{user_id}\"\n" \
               f"joke: \"{joke_text}\"\n"
        text_writer(text, dir_jokes)

        # logger
        log_txt = f"[ joke -> button 'submit joke' ] New joke was posted by {user_id}"
        log_info(log_txt)

        # metrics
        ui_counter.labels("modal", "joke", "submit")
        ui_counter.labels("modal", "joke", "submit").inc()

        # answer
        await interaction.response.send_message(joke_modal_submit_message, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, commands.BadArgument):
            ui_errors_counter.labels("modal", "joke", "BadArgument")
            ui_errors_counter.labels("modal", "joke", "BadArgument").inc()
            error_text = error.args[0]
            text = Colorizer(bad_argument.format(error_text)).colorize()
            await interaction.response.send_message(text, ephemeral=True)
