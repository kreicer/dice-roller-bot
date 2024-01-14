import discord
from discord.ext import commands

from functions.colorizer import Colorizer
from functions.config import dir_feedback, log_file, community_support, dev_github, topgg_link, community_policy
from functions.generators import generate_help_short_output, generate_commands_help, generate_action_short_output, \
    generate_postfix_short_output, generate_postfix_help, generate_action_help
from functions.workhorses import text_writer, logger
from lang.EN.buttons import community_help_feedback, community_help_support, community_about_policy
from lang.EN.errors import bad_argument
from lang.EN.ui import community_selector_all, community_selector_placeholder, community_modal_submit_feedback, \
    community_modal_text_feedback, community_modal_text_feedback_placeholder, community_modal_submit_message, \
    roll_selector_all, roll_selector_placeholder, action_selector_all, action_selector_placeholder
from models.actions import actions
from models.postfixes import postfixes
from models.commands import cmds, cogs
from models.metrics import ui_counter, ui_errors_counter


# SELECTOR for COMMANDS, ACTIONS and POSTFIXES UI
class TopicSelector(discord.ui.Select):
    def __init__(self, placeholder: str):
        topic_list = [
            discord.SelectOption(label="Commands", value="commands"),
            discord.SelectOption(label="Postfixes", value="postfixes"),
            discord.SelectOption(label="Actions", value="actions")
        ]
        super().__init__(custom_id="dr_help_selector_topics", placeholder=placeholder, min_values=1, max_values=1,
                         options=topic_list, row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        topic = self.values[0]
        if topic == "postfixes":
            result = generate_postfix_short_output()
            new_view = PostfixView()
        elif topic == "actions":
            result = generate_action_short_output()
            new_view = ActionsView()
        else:
            result = generate_help_short_output(cogs)
            new_view = HelpView()

        ui_counter.labels("selector", "help", "topics")
        ui_counter.labels("selector", "help", "topics").inc()
        await interaction.response.edit_message(content=result, view=new_view)


# MODAL for BUTTON "Submit Feedback"
class SubmitFeedback(discord.ui.Modal, title=community_modal_submit_feedback):
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
        user_id = interaction.user.id
        feedback = self.feedback_text.value

        text = f"username: \"{user_id}\"\n" \
               f"feedback: \"{feedback}\"\n"
        text_writer(text, dir_feedback)

        log_txt = f"[ feedback -> button 'submit feedback' ] New feedback was posted by {user_id}"
        logger(log_file, "INFO", log_txt)
        ui_counter.labels("modal", "help", "feedback")
        ui_counter.labels("modal", "help", "feedback").inc()
        await interaction.response.send_message(community_modal_submit_message, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, commands.BadArgument):
            ui_errors_counter.labels("modal", "help", "BadArgument")
            ui_errors_counter.labels("modal", "help", "BadArgument").inc()
            error_text = error.args[0]
            text = Colorizer(bad_argument.format(error_text)).colorize()
            await interaction.response.send_message(text, ephemeral=True)


# BUTTON for COMMANDS, ACTIONS and POSTFIXES UI
class FeedbackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label=community_help_feedback, style=discord.ButtonStyle.gray,
                         emoji="📝", row=3, custom_id="dr_help_button_feedback")

    async def callback(self, interaction: discord.Interaction) -> None:
        modal = SubmitFeedback()
        ui_counter.labels("button", "help", "feedback")
        ui_counter.labels("button", "help", "feedback").inc()
        await interaction.response.send_modal(modal)


# ABOUT UI
class AboutView(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(discord.ui.Button(label="Github", style=discord.ButtonStyle.link,
                                        url=dev_github, emoji="🧑‍💻"))
        self.add_item(discord.ui.Button(label="Top.gg", style=discord.ButtonStyle.link,
                                        url=topgg_link, emoji="👍"))
        self.add_item(discord.ui.Button(label=community_about_policy, style=discord.ButtonStyle.link,
                                        url=community_policy, emoji="🔏"))


# COMMANDS UI
class HelpView(discord.ui.View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(TopicSelector(placeholder="Commands"))
        self.add_item(FeedbackButton())
        self.add_item(discord.ui.Button(label=community_help_support, style=discord.ButtonStyle.link,
                                        url=community_support, emoji="🆘", row=3))
        self.message = None

    # async def on_timeout(self) -> None:
    #    await self.message.edit(view=None)

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

    @discord.ui.select(placeholder=community_selector_placeholder, min_values=1, max_values=1,
                       options=options_list, row=2, custom_id="dr_help_selector_commands")
    async def _command_selector(self, interaction: discord.Interaction, select: discord.ui.Select):
        command = select.values[0]
        if command == "all":
            result = generate_help_short_output(cogs)
        else:
            result = generate_commands_help(command)
        ui_counter.labels("selector", "help", "details")
        ui_counter.labels("selector", "help", "details").inc()
        await interaction.response.edit_message(content=result)


# POSTFIX UI
class PostfixView(discord.ui.View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(TopicSelector(placeholder="Postfixes"))
        self.add_item(FeedbackButton())
        self.add_item(discord.ui.Button(label=community_help_support, style=discord.ButtonStyle.link,
                                        url=community_support, emoji="🆘", row=3))
        self.message = None

    postfixes_list = []
    for item in postfixes.keys():
        if postfixes[item]["enabled"]:
            postfixes_list.append(item)
    options_list = []
    for item in postfixes_list:
        opt = discord.SelectOption(label=postfixes[item]["name"], value=item)
        options_list.append(opt)
    all = discord.SelectOption(label=roll_selector_all, value="all")
    options_list.insert(0, all)

    @discord.ui.select(placeholder=roll_selector_placeholder, min_values=1, max_values=1, options=options_list,
                       row=2, custom_id="dr_postfix_selector_postfix")
    async def _postfix_selector(self, interaction: discord.Interaction, select: discord.ui.Select):
        postfix = select.values[0]
        if postfix == "all":
            result = generate_postfix_short_output()
        else:
            result = generate_postfix_help(postfix.lower())
        ui_counter.labels("selector", "postfix", "details")
        ui_counter.labels("selector", "postfix", "details").inc()
        await interaction.response.edit_message(content=result)


# ACTION UI
class ActionsView(discord.ui.View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(TopicSelector(placeholder="Actions"))
        self.add_item(FeedbackButton())
        self.add_item(discord.ui.Button(label=community_help_support, style=discord.ButtonStyle.link,
                                        url=community_support, emoji="🆘", row=3))
        self.message = None

    # async def on_timeout(self) -> None:
    #    await self.message.edit(view=None)

    action_list = []
    for item in actions.keys():
        if actions[item]["enabled"]:
            action_list.append(item)
    options_list = []
    for item in action_list:
        opt = discord.SelectOption(label=item, value=item)
        options_list.append(opt)
    all = discord.SelectOption(label=action_selector_all, value="all")
    options_list.insert(0, all)

    @discord.ui.select(placeholder=action_selector_placeholder, min_values=1, max_values=1, options=options_list,
                       row=2, custom_id="dr_action_selector_action")
    async def _postfix_selector(self, interaction: discord.Interaction, select: discord.ui.Select):
        action = select.values[0]
        if action == "all":
            result = generate_action_short_output()
        else:
            result = generate_action_help(action.lower())
        ui_counter.labels("selector", "action", "details")
        ui_counter.labels("selector", "action", "details").inc()
        await interaction.response.edit_message(content=result)
