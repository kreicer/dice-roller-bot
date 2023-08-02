import traceback
import discord

from functions.config import dir_feedback, log_file
from functions.workhorses import text_writer, logger
from models.metrics import ui_button_counter, ui_modals_counter
from models.postfixes import postfixes


class Feedback(discord.ui.Modal, title="Feedback"):
    username = discord.ui.TextInput(
        label="Username",
        style=discord.TextStyle.short,
        placeholder="Username (your or any)",
        required=True,
        min_length=3,
        max_length=30,
        row=1
    )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        traceback.print_exception(type(error), error, error.__traceback__)
        await interaction.response.send_message("Something went wrong...", ephemeral=True)


class Postfix(Feedback, title="Postfix feedback"):
    # for the better times
    # postfixes_list = list(postfixes.keys())
    # postfixes_list.append("New postfix")
    # options_list = []
    # for item in postfixes_list:
    #    opt = discord.SelectOption(label=item)
    #    options_list.append(opt)
    # postfix = discord.ui.Select(
    #    custom_id="feedback_postfix_selector",
    #    placeholder="Select the postfix",
    #    min_values=1,
    #    max_values=1,
    #    row=2,
    #    disabled=False,
    #    options=options_list
    #    #options=list(postfixes.keys())
    # )

    postfix = discord.ui.TextInput(
        label="Postfix",
        style=discord.TextStyle.short,
        placeholder="Postfix (existing or new one)",
        required=True,
        min_length=1,
        max_length=10,
        row=2
    )

    feedback = discord.ui.TextInput(
        label="Feedback",
        style=discord.TextStyle.long,
        placeholder="Feedback (bug or improvement)",
        required=True,
        min_length=3,
        max_length=3000,
        row=3
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # add function to post into files
        username = self.username.value
        postfix = self.postfix.value
        feedback = self.feedback.value

        text = f"username: \"{username}\"\n" \
               f"postfix: \"{postfix}\"\n" \
               f"feedback: \"{feedback}\""
        text_writer(text, dir_feedback)

        log_txt = f"[ postfixes -> button 'feedback' ] New feedback was posted by {username}"
        logger(log_file, "INFO", log_txt)
        ui_modals_counter.labels("postfix", "feedback")
        ui_modals_counter.labels("postfix", "feedback").inc()
        await interaction.response.send_message("Thanks for your feedback!", ephemeral=True)


class PostfixView(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Feedback", style=discord.ButtonStyle.green, emoji="📝")
    async def _report_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = Postfix()
        ui_button_counter.labels("postfix", "feedback")
        ui_button_counter.labels("postfix", "feedback").inc()
        await interaction.response.send_modal(modal)


view = PostfixView()
view.add_item(discord.ui.Button(label="invite me!", style=discord.ButtonStyle.link,
                                url="http://discord.gg/cj3fSYZzKQ", emoji="🥂"))
