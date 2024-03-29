import asyncio
from typing import List

import discord
from discord import app_commands
import traceback

from discord.ext import commands

from functions.actions import detect_action_type
from functions.colorizer import Colorizer
from functions.logging import log_error
from lang.EN.errors import bot_missing_permissions, bad_argument, argument_parsing_error, throws_groups_error_text, \
    missing_required_argument, cmd_on_cooldown
from lang.EN.texts import command_roll_parameter
from models.commands import cmds
from models.regexp import parsing_regexp as regexp
from models.limits import group_limit as g_limit, visual_dice_label_limit as label_limit
from models.metrics import commands_counter, errors_counter, buckets_counter, action_counter
from functions.workhorses import (
    split_on_dice,
    split_on_parts,
    dice_roll,
    fate_roll,
    calc_result,
    fate_result,
    add_mod_result,
    sub_mod_result, check_if_shortcut, split_dice_actions, get_autocomplete, update_stat, update_autocomplete
)
from functions.postfixes import postfix_magick, postfix_check
from functions.checks import check_limit, check_multiply
from functions.visualizers import (
    make_subzero,
    fate_subzero,
    dice_maker,
    convert_dice_for_output,
    body_for_output,
    create_table
)


# ROLL COG
class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ROLL COMMAND
    @commands.hybrid_command(name=cmds["roll"]["name"], brief=cmds["roll"]["brief"], aliases=cmds["roll"]["aliases"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(2, 1, commands.BucketType.user)
    async def _roll(self, ctx: commands.Context, *,
                    rolls: str = commands.parameter(description=command_roll_parameter)) -> None:
        overall = ""
        args = str(rolls).split()
        args_len = len(args)
        error_text = throws_groups_error_text.format(args_len, g_limit)
        check_limit(args_len, g_limit, error_text)
        user_id = str(ctx.message.author.id)
        try:
            discord_id = str(ctx.guild.id)
            guild = True
        except AttributeError:
            discord_id = str(ctx.channel.id)
            guild = False
        bucket_id = 1
        for bucket in args:
            result_sum = 0
            visual_list = []
            visual_bucket = ""

            cleared_bucket, actions = split_dice_actions(bucket)
            if actions:
                tag = ""
                label = ""
                for action in actions:
                    action_type, value = detect_action_type(action)
                    if action_type == 1:
                        future_len = len(args) + value - 1
                        check_multiply(future_len)
                        counter = 1
                        while counter < value:
                            args.insert(bucket_id, cleared_bucket)
                            counter += 1
                        args_len = len(args)
                        action_counter.labels("multiplier")
                        action_counter.labels("multiplier").inc()
                    elif action_type == 2:
                        # TODO: member intents and find mechanism
                        tag += "<" + value + ">" + "\n"
                        action_counter.labels("tag")
                        action_counter.labels("tag").inc()
                    else:
                        label = "<pink>" + value + "<end>" + "\n"
                        # label += Colorizer(value).colorize()
                        action_counter.labels("label")
                        action_counter.labels("label").inc()
                overall += tag + label
            bucket = check_if_shortcut(discord_id, user_id, cleared_bucket)
            bucket = bucket.lower()
            list_of_dice = split_on_dice(bucket)
            for dice in list_of_dice:
                # dice split
                dice_parts = split_on_parts(dice, regexp)
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

                if guild and dice_parts["type"] != 0:
                    dice_number = len(throws_result_list)
                    update_stat(discord_id, dice_number, 0)
                if dice_parts["type"] != 0:
                    dice_number = len(throws_result_list)
                    update_stat(user_id, dice_number, 1)

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

            visual_bucket = convert_dice_for_output(visual_bucket, label_limit)
            rolls_output, result_output, rolls_column, result_column = body_for_output(visual_list, result_sum)
            table = create_table(visual_bucket, rolls_output, result_output, rolls_column, result_column)
            # table = table.replace(" 1 ", " <yellow>1<end>")
            # table = Colorizer(table).colorize()
            # await ctx.send(table)
            # sub_overall = f"```{table}```"
            overall += f"{table}" + "\n"
            bucket_id += 1
            update_autocomplete(user_id, bucket)

        await ctx.defer()

        # metrics
        buckets_counter.labels(args_len)
        buckets_counter.labels(args_len).inc()
        commands_counter.labels("roll")
        commands_counter.labels("roll").inc()

        overall = Colorizer(overall).colorize()
        if args_len > 6:
            await asyncio.sleep(5)
        await ctx.send(overall)

    @_roll.autocomplete(name="rolls")
    async def _roll_autocomplete(self, interaction: discord.Interaction, current: str) \
            -> List[app_commands.Choice[str]]:
        user_id = interaction.user.id
        dice = get_autocomplete(user_id)
        return [
            app_commands.Choice(name=rolls, value=rolls)
            for rolls in dice if current.lower() in rolls.lower()
        ]

    # ROLL ERRORS HANDLER
    @_roll.error
    async def _roll_error(self, ctx, error):
        prefix = ctx.prefix
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("roll", "BotMissingPermissions")
            errors_counter.labels("roll", "BotMissingPermissions").inc()
            text = Colorizer(bot_missing_permissions).colorize()
            dm = await ctx.author.create_dm()
            await dm.send(text)
        elif isinstance(error, commands.MissingRequiredArgument):
            errors_counter.labels("roll", "MissingRequiredArgument")
            errors_counter.labels("roll", "MissingRequiredArgument").inc()
            text = Colorizer(missing_required_argument.format(prefix)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        elif isinstance(error, commands.BadArgument):
            errors_counter.labels("roll", "BadArgument")
            errors_counter.labels("roll", "BadArgument").inc()
            error_text = error.args[0]
            text = Colorizer(bad_argument.format(error_text)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        elif isinstance(error, commands.ArgumentParsingError):
            errors_counter.labels("roll", "ArgumentParsingError")
            errors_counter.labels("roll", "ArgumentParsingError").inc()
            error_text = error.args[0]
            text = Colorizer(argument_parsing_error.format(error_text)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        elif isinstance(error, commands.CommandOnCooldown):
            errors_counter.labels("roll", "CommandOnCooldown")
            errors_counter.labels("roll", "CommandOnCooldown").inc()
            retry = round(error.retry_after, 2)
            text = Colorizer(cmd_on_cooldown.format(retry)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        else:
            traceback.print_exception(type(error), error, error.__traceback__)
            text = type(error) + error + error.__traceback__
            log_error(text)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Roll(bot))
