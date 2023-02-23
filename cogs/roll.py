import asyncio

from discord.ext import commands  # , tasks
from models.commands import roll as roll, postfix as pw
from models.regexp import parsing_regexp as regexp
from models.limits import group_limit as g_limit, visual_dice_label_limit as label_limit
# from functions.workhorses import generate_dicts as gen_dicts
from functions.workhorses import (
    split_on_dice,
    split_on_parts,
    dice_roll,
    calc_result,
    add_mod_result,
    sub_mod_result,
    make_pw_list
)
from functions.postfixes import postfix_magick
from functions.checks import check_limit
from functions.visualizers import make_subzero, dice_maker, convert_dice_for_output, body_for_output, create_table


# roll cog
class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.generate_aliases.start()

    # @tasks.loop(hours=24)
    # async def generate_aliases(self):
    #    postfix_list = gen_dicts(pfs_dict)
    #    return postfix_list

    @commands.hybrid_command(name=roll["name"], brief=roll["brief"], help=roll["help"], aliases=roll["aliases"],
                             with_app_command=True)
    async def _roll(self, ctx: commands.Context, *,
                    rolls: str = commands.parameter(description="Place dice here, split with whitespace")) -> None:
        overall = ""
        args = rolls.split()
        args_len = len(args)
        error_text = f"Number of throw groups ({args_len}) is greater than the current limit of {g_limit}"
        check_limit(args_len, g_limit, error_text)
        for bucket in args:
            result_sum = 0
            visual_list = []
            visual_bucket = ""
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
                else:
                    throws_result_list_before_postfix = dice_roll(dice_parts["throws"], dice_parts["edge"])
                    throws_result_list = postfix_magick(throws_result_list_before_postfix, dice_parts)
                    sub_sum = calc_result(throws_result_list)

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
                    throws_result_list = make_subzero(throws_result_list)
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
        # await ctx.defer(ephemeral=True)
        await ctx.defer()
        if args_len > 5:
            await asyncio.sleep(5)
        await ctx.send(overall)

    @commands.hybrid_command(name=pw["name"], brief=pw["brief"], help=pw["help"], aliases=pw["aliases"],
                             with_app_command=True)
    async def _power_words(self, ctx: commands.Context) -> None:
        pw_list = make_pw_list(ctx.prefix)
        await ctx.defer(ephemeral=True)
        await ctx.send(pw_list)

    # PREFIX SET ERRORS HANDLER
    @_roll.error
    async def _roll_error(self, ctx, error):
        prefix = ctx.prefix
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Bot Missing Permissions**\n'
                           f'Dice Roller have missing permissions to answer you in this channel.\n'
                           f'You can solve it by adding rights in channel or server management section.')
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Missing Required Argument**\n'
                           f'You should to specify one valid dice at least.'
                           f'Try something like: ```{prefix}roll 4d20/dl:1+3```')
        if isinstance(error, commands.BadArgument):
            error_text = error.args[0]
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Bad Argument**\n'
                           f'{error_text}')
        if isinstance(error, commands.ArgumentParsingError):
            error_text = error.args[0]
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Argument Parsing Error**\n'
                           f'{error_text}')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Roll(bot))