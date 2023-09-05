import asyncio

import discord
from discord.ext import commands  # , tasks
from models.commands import cmds
from models.postfixes import postfixes
from models.regexp import parsing_regexp as regexp
from models.limits import group_limit as g_limit, visual_dice_label_limit as label_limit
from models.metrics import commands_counter, errors_counter, ui_selects_counter
# from functions.workhorses import generate_dicts as gen_dicts
from functions.workhorses import (
    split_on_dice,
    split_on_parts,
    DiceBucket,
    generate_postfix_short_output, generate_postfix_help
)
from functions.postfixes import postfix_magick
from functions.checks import check_limit
from functions.visualizers import (
    make_subzero,
    fate_subzero,
    dice_maker,
    convert_dice_for_output,
    body_for_output,
    create_table
)


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
    all = discord.SelectOption(label="List postfixes", value="all")
    options_list.insert(0, all)

    @discord.ui.select(placeholder="Select the postfix...", min_values=1, max_values=1, options=options_list)
    async def _postfix_selector(self, interaction: discord.Interaction, select: discord.ui.Select):
        postfix = select.values[0]
        if postfix == "all":
            result = generate_postfix_short_output()
        else:
            result = generate_postfix_help(postfix.lower())
        ui_selects_counter.labels("postfix", postfix)
        ui_selects_counter.labels("postfix", postfix).inc()
        await interaction.response.edit_message(content=result)


# ROLL COG
class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.generate_aliases.start()

    # @tasks.loop(hours=24)
    # async def generate_aliases(self):
    #    postfix_list = gen_dicts(pfs_dict)
    #    return postfix_list

    # ROLL COMMAND
    @commands.hybrid_command(name=cmds["roll"]["name"], brief=cmds["roll"]["brief"], aliases=cmds["roll"]["aliases"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
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
                else:
                    roller = DiceBucket(dice_parts)
                    roller.roll()
                    throws_result_list = roller.text()
                    sub_sum = roller.sum()

                # dice summarize
                if dice_parts["mod"] == "-":
                    result_sum -= sub_sum
                else:
                    result_sum += sub_sum
                # dice visualize
                args = [dice_parts["mod"], dice_parts["throws"]]
                if dice_parts["type"] > 0:
                    args.extend(["d", dice_parts["edge"]])
                if "postfix" in dice_parts.keys():
                    args.extend(["/", dice_parts["postfix"], ":", dice_parts["value"]])
                visual_dice = dice_maker(*args)
                visual_bucket += visual_dice
                if dice_parts["mod"] == "-":
                    if dice_parts["type"] < 3:
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
        # await ctx.defer(ephemeral=True)
        await ctx.defer()
        if args_len > 5:
            await asyncio.sleep(5)
        await ctx.send(overall)

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
        await ctx.send(result, view=view)

    # ROLL ERRORS HANDLER
    @_roll.error
    async def _roll_error(self, ctx, error):
        prefix = ctx.prefix
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("roll", "BotMissingPermissions")
            errors_counter.labels("roll", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')
        if isinstance(error, commands.MissingRequiredArgument):
            errors_counter.labels("roll", "MissingRequiredArgument")
            errors_counter.labels("roll", "MissingRequiredArgument").inc()
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Missing Required Argument**\n'
                           f'You should to specify one valid dice at least.'
                           f'Try something like: ```{prefix}roll 4d20/dl:1+3```')
        if isinstance(error, commands.BadArgument):
            errors_counter.labels("roll", "BadArgument")
            errors_counter.labels("roll", "BadArgument").inc()
            error_text = error.args[0]
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Bad Argument**\n'
                           f'{error_text}')
        if isinstance(error, commands.ArgumentParsingError):
            errors_counter.labels("roll", "ArgumentParsingError")
            errors_counter.labels("roll", "ArgumentParsingError").inc()
            error_text = error.args[0]
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Argument Parsing Error**\n'
                           f'{error_text}')

    # POSTFIX ERRORS HANDLER
    @_postfix.error
    async def _postfix_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("postfix", "BotMissingPermissions")
            errors_counter.labels("postfix", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')
        if isinstance(error, commands.BadArgument):
            errors_counter.labels("postfix", "BadArgument")
            errors_counter.labels("postfix", "BadArgument").inc()
            error_text = error.args[0]
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Bad Argument**\n'
                           f'{error_text}')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Roll(bot))
