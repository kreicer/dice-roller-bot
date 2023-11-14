import asyncio
# import traceback

import discord
from discord.ext import commands

from functions.colorizer import Colorizer
from functions.postfixes import postfix_check, postfix_magick
from functions.visualizers import dice_maker, make_subzero, fate_subzero, convert_dice_for_output, body_for_output, \
    create_table
from functions.workhorses import split_on_dice, split_on_parts, dice_roll, calc_result, fate_roll, fate_result, \
    sub_mod_result, add_mod_result
from lang.EN.errors import throws_groups_error_spec
from models.regexp import parsing_regexp
from models.limits import group_limit, visual_dice_label_limit
from models.metrics import commands_counter
from ui.context import SubmitBug


# CONTEXT COMMANDS COG
async def _context_roll(interaction: discord.Interaction, message: discord.Message):
    text = message.content
    overall = ""
    words = str(text).split()
    dice_for_roll = []
    for word in words:
        try:
            dice_dict = {}
            list_of_dice = split_on_dice(word)
            for dice in list_of_dice:
                dice_dict = split_on_parts(dice, parsing_regexp)
            if dice_dict["type"] != 0:
                dice_for_roll.append(word)
        except Exception as e:
            # traceback.print_exception(type(e), e, e.__traceback__)
            pass
    dice_amount = len(dice_for_roll)
    error_text = Colorizer(throws_groups_error_spec.format(dice_amount, group_limit)).colorize()
    if dice_amount > group_limit:
        await interaction.response.send_message(error_text, ephemeral=True)
    elif dice_amount > 0:
        for d in dice_for_roll:
            result_sum = 0
            visual_list = []
            visual_bucket = ""
            list_of_dice = split_on_dice(d)
            for dice in list_of_dice:
                # dice split
                dice_parts = split_on_parts(dice, parsing_regexp)
                # dice rolls
                if dice_parts["type"] == 0:
                    throws_result_list = [dice_parts["throws"]]
                    sub_sum = dice_parts["throws"]
                elif dice_parts["type"] == 1:
                    throws_result_list = dice_roll(dice_parts["throws"], dice_parts["edge"])
                    sub_sum = calc_result(throws_result_list)
                elif dice_parts["type"] == 3:
                    throws_result_list = fate_roll(dice_parts["throws"])
                    sub_sum = fate_result(throws_result_list)
                else:
                    throws_result_list_before_postfix = dice_roll(dice_parts["throws"], dice_parts["edge"])
                    postfix_check(dice_parts)
                    throws_result_list, sub_sum = postfix_magick(throws_result_list_before_postfix, dice_parts)

                # dice summarize
                if dice_parts["mod"] == "-":
                    result_sum = sub_mod_result(result_sum, sub_sum)
                else:
                    result_sum = add_mod_result(result_sum, sub_sum)
                # dice visualize
                visual_dice = dice_maker(dice_parts["mod"], dice_parts["throws"], "d", dice_parts["edge"], "/",
                                         dice_parts["postfix"], ":", dice_parts["value"])
                visual_bucket += visual_dice
                if dice_parts["mod"] == "-":
                    if dice_parts["type"] != 3:
                        throws_result_list = make_subzero(throws_result_list)
                        visual_list += throws_result_list
                    else:
                        throws_result_list = fate_subzero(throws_result_list)
                        visual_list += throws_result_list
                else:
                    visual_list += throws_result_list

            # bucket visualize
            if visual_bucket.startswith("+"):
                visual_bucket = visual_bucket[1:]

            visual_bucket = convert_dice_for_output(visual_bucket, visual_dice_label_limit)
            rolls_output, result_output, rolls_column, result_column = body_for_output(visual_list, result_sum)
            table = create_table(visual_bucket, rolls_output, result_output, rolls_column, result_column)
            sub_overall = f"```{table}```"
            overall += sub_overall

        commands_counter.labels("ttr")
        commands_counter.labels("ttr").inc()
        await interaction.response.defer()
        if dice_amount > 6:
            await asyncio.sleep(5)
        await interaction.followup.send(overall)
    else:
        await interaction.response.send_message("No dice or bad dice in text", ephemeral=True)


async def _report(interaction: discord.Interaction, message: discord.Message):
    technical_info = str(interaction.data)
    modal = SubmitBug(technical_info)
    commands_counter.labels("report")
    commands_counter.labels("report").inc()
    await interaction.response.send_modal(modal)


class ContextCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.ctx_t2r = discord.app_commands.ContextMenu(
            name="Text to Roll",
            callback=_context_roll
        )
        self.ctx_report = discord.app_commands.ContextMenu(
            name="Report Bug",
            callback=_report
        )
        self.bot.tree.add_command(self.ctx_t2r)
        self.bot.tree.add_command(self.ctx_report)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ContextCommands(bot))
