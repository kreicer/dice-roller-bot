import discord
from discord.ext import commands

from functions.colorizer import Colorizer
from functions.config import dir_feedback, log_file
from functions.generators import generate_help_short_output, generate_commands_help
from functions.workhorses import text_writer, logger
from lang.EN.buttons import community_help_feedback
from lang.EN.errors import bad_argument
from lang.EN.ui import community_selector_all, community_selector_placeholder, community_modal_submit_feedback, \
    community_modal_text_user, community_modal_text_user_placeholder, community_modal_text_feedback, \
    community_modal_text_feedback_placeholder, community_modal_submit_message
from models.commands import cmds, cogs
from models.metrics import ui_modals_counter, errors_counter, ui_selects_counter, ui_button_counter


# ABOUT UI
class AboutView(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)


# HELP UI
class HelpView(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    cmd_list = []
    for item in cmds.keys():
        if cmds[item]["enabled"]:
            cmd_list.append(item)
    options_list = []
    for item in cmd_list:
        opt = discord.SelectOption(label=cmds[item]["name"], value=item)
        options_list.append(opt)
    all = discord.SelectOption(label=community_selector_all, value="all")
    options_list.insert(0, all)

    @discord.ui.select(placeholder=community_selector_placeholder, min_values=1, max_values=1, options=options_list)
    async def _command_selector(self, interaction: discord.Interaction, select: discord.ui.Select):
        command = select.values[0]
        if command == "all":
            result = generate_help_short_output(cogs)
        else:
            result = generate_commands_help(command)
        ui_selects_counter.labels("command", command)
        ui_selects_counter.labels("command", command).inc()
        await interaction.response.edit_message(content=result)

    @discord.ui.button(label=community_help_feedback, style=discord.ButtonStyle.blurple, emoji="📝")
    async def _submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = SubmitFeedback()
        ui_button_counter.labels("feedback", "submit")
        ui_button_counter.labels("feedback", "submit").inc()
        await interaction.response.send_modal(modal)


class SubmitFeedback(discord.ui.Modal, title=community_modal_submit_feedback):
    username = discord.ui.TextInput(
        label=community_modal_text_user,
        style=discord.TextStyle.short,
        placeholder=community_modal_text_user_placeholder,
        required=True,
        min_length=3,
        max_length=30,
        row=1
    )

    feedback_text = discord.ui.TextInput(
        label=community_modal_text_feedback,
        style=discord.TextStyle.long,
        placeholder=community_modal_text_feedback_placeholder,
        required=True,
        min_length=10,
        max_length=3000,
        row=2
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        username = self.username.value
        feedback = self.feedback_text.value

        text = f"username: \"{username}\"\n" \
               f"feedback: \"{feedback}\"\n"
        text_writer(text, dir_feedback)

        log_txt = f"[ feedback -> button 'submit feedback' ] New feedback was posted by {username}"
        logger(log_file, "INFO", log_txt)
        ui_modals_counter.labels("feedback", "submit")
        ui_modals_counter.labels("feedback", "submit").inc()
        await interaction.response.send_message(community_modal_submit_message, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, commands.BadArgument):
            errors_counter.labels("feedback", "BadArgument")
            errors_counter.labels("feedback", "BadArgument").inc()
            error_text = error.args[0]
            text = Colorizer(bad_argument.format(error_text)).colorize()
            await interaction.response.send_message(text, ephemeral=True)
