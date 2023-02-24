from discord.ext import commands
from functions.workhorses import text_writer, logger
from functions.config import feedback_dir, log_file
from models.commands import feedback as fdk, hello as hl


# for future version
# class MyHelp(commands.HelpCommand):
#     async def send_bot_help(self, mapping):
#         body = ""
#         for cog, cmds in mapping.items():
#             command_signatures = [self.get_command_signature(c) for c in cmds]
#             if command_signatures:
#                 cog_name = getattr(cog, "qualified_name", "No Category")
#                 body += f"{cog_name}:\n" \
#                        f"{command_signatures}\n"
#         help_output = f"```{body}```"
#
#         channel = self.get_destination()
#         await channel.send(help_output)
#
# !help <command>
#    async def send_command_help(self, command):
#        await self.context.send("This is help command")
#
#  !help <group>
#    async def send_group_help(self, group):
#        await self.context.send("This is help group")
#
# !help <cog>
#    async def send_cog_help(self, cog):
#        await self.context.send("This is help cog")


# Community COG
class Community(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
# for future version
#        self._original_help_command = bot.help_command
#        bot.help_command = MyHelp()
#        bot.help_command.cog = self

#    def cog_unload(self):
#        self.bot.help_command = self._original_help_command

    @commands.hybrid_command(name=fdk["name"], brief=fdk["brief"], help=fdk["help"], aliases=fdk["aliases"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _send_feedback(self, ctx: commands.Context, *, feedback: str) -> None:
        author = ctx.message.author
        # TODO: migrate directory name to config, add check on exist, if not - create
        feedback = "\"" + feedback + "\""
        text_writer(feedback, feedback_dir)

        log_txt = "New feedback was posted by " + str(author)
        logger(log_file, "INFO", log_txt)

        await ctx.defer(ephemeral=True)
        await ctx.send(f'Thank you for the feedback!')

    @commands.hybrid_command(name=hl["name"], brief=hl["brief"], help=hl["help"], aliases=hl["aliases"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _hello(self, ctx: commands.Context) -> None:
        hello_text = "Hello, friend!\n" \
                     "My name is Dice Roller. I will be your guide in this awesome adventure. " \
                     "First of all, my core functionality - roll any dice you can image. " \
                     "And be you useful helper on this way, of course. " \
                     "I recommend start from something simple... Make a d20 dice roll!\n\n" \
                     "**Rolls and Power Words**\n" \
                     "You can roll simple dice, complex dice with multipliers and also with Power Words! " \
                     "Let me show you some examples...\n\n" \
                     "Your command should start from slash (/), local bot prefix or bot mention. " \
                     "Next part - command name. In our case it will be \"roll\" or just \"r\". Yep. whitespace next. " \
                     "And from this moment only you decide what  you want to roll. " \
                     "Dice may be simple like 2d20 or complex like 3d8+d4-1. " \
                     "Dice may contain Power Words. I will provide this as example - 4d8/dl:2. " \
                     "Now i show you best part. You can combine any dice and roll more than one dice per command." \
                     "```/roll 3d6+d4 3d20/dh 2d20+2d4/dl:1-1```\n" \
                     "Few words about Power Words... You can get full available list with command.```/powerwords```"
        await ctx.defer(ephemeral=True)
        await ctx.send(hello_text)

    # FEEDBACK ERRORS HANDLER
    @_send_feedback.error
    async def _send_feedback_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            log_txt = "File exist already "
            logger(log_file, "ERROR", log_txt)
            await ctx.defer(ephemeral=True)
            await ctx.send(f'Something wrong on our end.')
        if isinstance(error, commands.MissingRequiredArgument):
            prefix = ctx.prefix
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Missing Required Argument**\n'
                           f'You should to write feedback message.'
                           f'Try something like: ```{prefix}feedback Awesome bot!```')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Community(bot))
