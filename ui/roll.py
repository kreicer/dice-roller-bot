import discord

from functions.generators import generate_postfix_short_output, generate_postfix_help
from lang.EN.ui import roll_selector_all, roll_selector_placeholder
from models.metrics import ui_selects_counter
from models.postfixes import postfixes


# POSTFIX UI
class PostfixSelector(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

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
        ui_selects_counter.labels("postfix", postfix)
        ui_selects_counter.labels("postfix", postfix).inc()
        await interaction.response.edit_message(content=result)
