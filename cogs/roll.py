import asyncio
import traceback

import discord
from discord import app_commands
from discord.ext import commands
from functions.colorizer import Colorizer
from lang.EN.errors import bot_missing_permissions, bad_argument, argument_parsing_error, throws_groups_error_text, \
    missing_required_argument, throws_groups_error_spec, bad_argument_spec
from lang.EN.texts import command_roll_parameter
from models.commands import cmds
from models.regexp import parsing_regexp as regexp
from models.limits import group_limit as g_limit, visual_dice_label_limit as label_limit
from models.metrics import commands_counter, errors_counter, buckets_counter
from functions.workhorses import (
    split_on_dice,
    split_on_parts,
    dice_roll,
    fate_roll,
    calc_result,
    fate_result,
    add_mod_result,
    sub_mod_result, check_if_shortcut
)
from functions.generators import generate_postfix_short_output
from functions.postfixes import postfix_magick, postfix_check, multiplier
from functions.checks import check_limit
from functions.visualizers import (
    make_subzero,
    fate_subzero,
    dice_maker,
    convert_dice_for_output,
    body_for_output,
    create_table
)
from ui.roll import PostfixSelector, RollView


# ROLL COG
class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Text to Roll",
            callback=self._context_roll
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def _context_roll(self, interaction: discord.Interaction, message: discord.Message):
        text = message.content
        overall = ""
        words = str(text).split()
        dice_for_roll = []
        for word in words:
            try:
                list_of_dice = split_on_dice(word)
                for dice in list_of_dice:
                    split_on_parts(dice, regexp)
                dice_for_roll.append(word)
            except Exception as e:
                pass
        dice_amount = len(dice_for_roll)
        error_text = Colorizer(throws_groups_error_spec.format(dice_amount, g_limit)).colorize()
        if dice_amount > g_limit:
            await interaction.response.send_message(error_text, ephemeral=True)
        elif dice_amount > 0:
            for d in dice_for_roll:
                result_sum = 0
                visual_list = []
                visual_bucket = ""
                list_of_dice = split_on_dice(d)
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
                        if dice_parts["postfix"] == "x":
                            try:
                                dice_for_roll = multiplier(dice_for_roll, dice_parts)
                                dice_amount = len(dice_for_roll)
                            except commands.BadArgument:
                                error_text = Colorizer(bad_argument_spec.format(g_limit)).colorize()
                                await interaction.response.send_message(error_text, ephemeral=True)
                                return
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

                visual_bucket = convert_dice_for_output(visual_bucket, label_limit)
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

    # ROLL COMMAND
    @commands.hybrid_command(name=cmds["roll"]["name"], brief=cmds["roll"]["brief"], aliases=cmds["roll"]["aliases"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _roll(self, ctx: commands.Context, *,
                    rolls: str = commands.parameter(description=command_roll_parameter)) -> None:
        overall = ""
        args = str(rolls).split()
        args_len = len(args)
        error_text = throws_groups_error_text.format(args_len, g_limit)
        check_limit(args_len, g_limit, error_text)
        # metrics
        buckets_counter.labels(args_len)
        buckets_counter.labels(args_len).inc()
        for bucket in args:
            result_sum = 0
            visual_list = []
            visual_bucket = ""
            try:
                discord_id = str(ctx.guild.id)
            except AttributeError:
                discord_id = str(ctx.channel.id)
            bucket = check_if_shortcut(discord_id, bucket)
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
                    if dice_parts["postfix"] == "x":
                        args = multiplier(args, dice_parts)
                        args_len = len(args)
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

            visual_bucket = convert_dice_for_output(visual_bucket, label_limit)
            rolls_output, result_output, rolls_column, result_column = body_for_output(visual_list, result_sum)
            table = create_table(visual_bucket, rolls_output, result_output, rolls_column, result_column)
            sub_overall = f"```{table}```"
            overall += sub_overall

        commands_counter.labels("roll")
        commands_counter.labels("roll").inc()
        await ctx.defer()
        if args_len > 6:
            await asyncio.sleep(5)
        view = RollView(overall, ctx.author)
        view.message = await ctx.send(overall, view=view)

    # POSTFIX COMMAND
    @commands.hybrid_command(name=cmds["postfix"]["name"], brief=cmds["postfix"]["brief"],
                             aliases=cmds["postfix"]["aliases"], with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _postfix(self, ctx: commands.Context) -> None:
        result = generate_postfix_short_output()

        commands_counter.labels("postfix")
        commands_counter.labels("postfix").inc()

        view = PostfixSelector()
        await ctx.defer(ephemeral=True)
        view.message = await ctx.send(result, view=view)

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
        if isinstance(error, commands.MissingRequiredArgument):
            errors_counter.labels("roll", "MissingRequiredArgument")
            errors_counter.labels("roll", "MissingRequiredArgument").inc()
            text = Colorizer(missing_required_argument.format(prefix)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        if isinstance(error, commands.BadArgument):
            errors_counter.labels("roll", "BadArgument")
            errors_counter.labels("roll", "BadArgument").inc()
            error_text = error.args[0]
            text = Colorizer(bad_argument.format(error_text)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        if isinstance(error, commands.ArgumentParsingError):
            errors_counter.labels("roll", "ArgumentParsingError")
            errors_counter.labels("roll", "ArgumentParsingError").inc()
            error_text = error.args[0]
            text = Colorizer(argument_parsing_error.format(error_text)).colorize()
            await ctx.defer(ephemeral=True)
            await ctx.send(text)
        # traceback.print_exception(type(error), error, error.__traceback__)

    # POSTFIX ERRORS HANDLER
    @_postfix.error
    async def _postfix_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("postfix", "BotMissingPermissions")
            errors_counter.labels("postfix", "BotMissingPermissions").inc()
            text = Colorizer(bot_missing_permissions).colorize()
            dm = await ctx.author.create_dm()
            await dm.send(text)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Roll(bot))
