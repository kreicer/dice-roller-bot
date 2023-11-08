import discord
from discord.ext import commands

from functions.colorizer import Colorizer
from functions.config import dir_bugs, log_file
from functions.workhorses import text_writer, logger
from lang.EN.errors import bad_argument
from models.metrics import ui_counter, ui_errors_counter


class SubmitBug(discord.ui.Modal):
    bug_description = discord.ui.TextInput(
        label="Bug description",
        style=discord.TextStyle.long,
        placeholder="Describe the bug in as much detail as possible",
        required=True,
        min_length=10,
        max_length=4000,
        row=1
    )

    def __init__(self, info):
        self.info = info
        super().__init__(title="Bug details")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # main
        user_id = interaction.user.id
        bug_description = self.bug_description.value
        text = f"\"{user_id}\"\n\n" \
               f"\"{bug_description}\"\n\n" \
               f"\"{self.info}\""
        text_writer(text, dir_bugs)

        # logger
        log_txt = f"[ context -> command 'report bug' ] Bug was reported by {user_id}"
        logger(log_file, "INFO", log_txt)

        # metrics
        ui_counter.labels("modal", "context", "report")
        ui_counter.labels("modal", "context", "report").inc()

        # answer
        await interaction.response.send_message("Thank you for the report!", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, commands.BadArgument):
            ui_errors_counter.labels("modal", "context", "BadArgument")
            ui_errors_counter.labels("modal", "context", "BadArgument").inc()
            error_text = error.args[0]
            text = Colorizer(bad_argument.format(error_text)).colorize()
            await interaction.response.send_message(text, ephemeral=True)
