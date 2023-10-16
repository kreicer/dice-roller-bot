import typing
import discord
from discord.ext import commands

from functions.generators import generate_postfix_short_output, generate_postfix_help
from functions.colorizer import Colorizer
from lang.EN.buttons import roll_roll_add_label
from lang.EN.errors import bad_argument, missing_permissions_spec
from lang.EN.ui import roll_selector_all, roll_selector_placeholder, roll_modal_add_label, roll_modal_text_label, \
    roll_modal_text_label_placeholder
from models.metrics import ui_counter, ui_errors_counter
from models.postfixes import postfixes


# POSTFIX UI
class PostfixSelector(discord.ui.View):
    def __init__(self, timeout=300):
        super().__init__(timeout=timeout)
        self.message = None

    async def on_timeout(self) -> None:
        await self.message.edit(view=None)

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

    @discord.ui.select(placeholder=roll_selector_placeholder, min_values=1, max_values=1, options=options_list)
    async def _postfix_selector(self, interaction: discord.Interaction, select: discord.ui.Select):
        postfix = select.values[0]
        if postfix == "all":
            result = generate_postfix_short_output()
        else:
            result = generate_postfix_help(postfix.lower())
        ui_counter.labels("selector", "postfix")
        ui_counter.labels("selector", "postfix").inc()
        await interaction.response.edit_message(content=result)


# ROLL UI
class RollView(discord.ui.View):
    def __init__(self, result: str, author: typing.Union[discord.Member, discord.User], timeout=300):
        self.message = None
        self.result = result
        self.author = author
        super().__init__(timeout=timeout)
        self.add_item(TagSomeone(result))

    async def on_timeout(self) -> None:
        await self.message.edit(view=None)

    # check user click vs user spawn
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            text = Colorizer(missing_permissions_spec).colorize()
            await interaction.response.send_message(text, ephemeral=True)
            return False
        return True

    @discord.ui.button(label=roll_roll_add_label, style=discord.ButtonStyle.gray, emoji="🏷️", row=2)
    async def _add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddLabel(self.result)

        # metrics
        ui_counter.labels("button", "roll")
        ui_counter.labels("button", "roll").inc()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.gray, emoji="🔒", row=2)
    async def _lock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # metrics
        ui_counter.labels("button", "roll")
        ui_counter.labels("button", "roll").inc()
        await interaction.response.edit_message(view=None)


class AddLabel(discord.ui.Modal):
    label = discord.ui.TextInput(
        label=roll_modal_text_label,
        style=discord.TextStyle.short,
        placeholder=roll_modal_text_label_placeholder,
        required=True,
        min_length=3,
        max_length=60,
        row=1
    )

    def __init__(self, result: str):
        self.result = result
        super().__init__(title=roll_modal_add_label)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        label = self.label.value
        prepare_label = "<pink>" + label + "<end>"
        color_label = Colorizer(prepare_label).colorize()
        labeled_result = color_label + self.result

        # metrics
        ui_counter.labels("modal", "roll")
        ui_counter.labels("modal", "roll").inc()
        await interaction.response.edit_message(content=labeled_result)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, commands.BadArgument):
            ui_errors_counter.labels("modal", "help", "BadArgument")
            ui_errors_counter.labels("modal", "help", "BadArgument").inc()
            error_text = error.args[0]
            text = Colorizer(bad_argument.format(error_text)).colorize()
            await interaction.response.send_message(text, ephemeral=True)


class TagSomeone(discord.ui.MentionableSelect):
    def __init__(self, result: str):
        # main
        self.result = result
        super().__init__(placeholder="Select someone to tag", min_values=0, max_values=3, row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        tagged = ""
        users = self.values
        for user in users:
            tagged += user.mention + " "
        txt = tagged + self.result
        if self.values:
            await interaction.response.edit_message(content=txt)
        else:
            await interaction.response.edit_message(content=self.result)

