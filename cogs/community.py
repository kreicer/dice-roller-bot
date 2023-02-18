import configparser

from discord.ext import commands

from functions.workhorses import text_writer, logger
from models.commands import feedback as fdk

# get params from config
config = configparser.ConfigParser()
config.read_file(open("config"))
log_file = config.get("logs", "log_file")
feedback_dir = config.get("dirs", "feedback_dir")

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

    # PREFIX SET ERRORS HANDLER
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
