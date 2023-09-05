import discord
from discord.ext import commands, tasks
from functions.workhorses import text_writer, logger, generate_info_output
from functions.config import dir_feedback, log_file, community_support, dev_github, topgg_link, community_policy
from models.commands import feedback as fdk, hello as hl, support as sup, about as ab
from models.metrics import commands_counter, errors_counter

guilds_number = 0


class AboutView(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)


# COMMUNITY COG
class Community(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self._update_servers_number.start()

    def cog_unload(self):
        self._update_servers_number.cancel()

    @tasks.loop(hours=1)
    async def _update_servers_number(self):
        global guilds_number
        guilds_number = len(self.bot.guilds)
        # Logger
        log_txt = "Guild number updated, current number: " + str(guilds_number)
        logger(log_file, "INFO", log_txt)

    @_update_servers_number.before_loop
    async def _before_update_servers_number(self):
        await self.bot.wait_until_ready()

    # ABOUT COMMAND
    @commands.hybrid_command(name=ab["name"], brief=ab["brief"], usage=ab["usage"], help=ab["help"],
                             aliases=ab["aliases"], with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _about(self, ctx: commands.Context) -> None:

        result = generate_info_output(guilds_number)

        view = AboutView()
        view.add_item(discord.ui.Button(label="Github", style=discord.ButtonStyle.link,
                                        url=dev_github, emoji="🧑‍💻"))
        view.add_item(discord.ui.Button(label="Top.gg", style=discord.ButtonStyle.link,
                                        url=topgg_link, emoji="👍"))
        view.add_item(discord.ui.Button(label="Privacy Policy", style=discord.ButtonStyle.link,
                                        url=community_policy, emoji="🔏"))

        commands_counter.labels("about")
        commands_counter.labels("about").inc()
        await ctx.defer(ephemeral=True)
        await ctx.send(result, view=view)

    # FEEDBACK COMMAND
    @commands.hybrid_command(name=fdk["name"], brief=fdk["brief"], help=fdk["help"], aliases=fdk["aliases"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def _send_feedback(self, ctx: commands.Context, *,
                             feedback: str = commands.parameter(description="Your feedback text")) -> None:
        author = ctx.message.author
        # TODO: migrate directory name to config, add check on exist, if not - create
        feedback = "\"" + feedback + "\""
        text_writer(feedback, dir_feedback)

        log_txt = "New feedback was posted by " + str(author)
        logger(log_file, "INFO", log_txt)

        commands_counter.labels("feedback")
        commands_counter.labels("feedback").inc()

        await ctx.defer(ephemeral=True)
        await ctx.send("Thank you for the feedback!")

    # HELLO COMMAND
    @commands.hybrid_command(name=hl["name"], brief=hl["brief"], help=hl["help"], aliases=hl["aliases"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def _hello(self, ctx: commands.Context) -> None:
        hello_text = ("Hello, friend!\n"
                      "My name is Dice Roller. I will be your guide in this awesome adventure. "
                      "First of all, my core functionality - roll any dice you can image. "
                      "And be you useful helper on this way, of course. "
                      "I recommend start from something simple... Make a d20 dice roll!\n\n"
                      "**Rolls and Postfixes**\n"
                      "You can roll simple dice, complex dice with multipliers and also with Postfixes! "
                      "Let me show you some examples...\n\n"
                      "Your command should start from slash (/), local bot prefix or bot mention. "
                      "Next part - command name. In our case it will be \"roll\" or just \"r\". Yep. whitespace next. "
                      "And from this moment only you decide what  you want to roll. "
                      "Dice may be simple like 2d20 or complex like 3d8+d4-1. "
                      "Dice may contain Postfix. I will provide this as example - 4d8/dl:2. "
                      "Now i show you best part. You can combine any dice and roll more than one dice per command."
                      "```/roll 3d6+d4 3d20/dh 2d20+2d4/dl:1-1```\n"
                      "Few words about Postfixes... You can get full available list with command.```/postfix```")

        commands_counter.labels("hello")
        commands_counter.labels("hello").inc()

        await ctx.defer(ephemeral=True)
        await ctx.send(hello_text)

    # SUPPORT COMMAND
    @commands.hybrid_command(name=sup["name"], brief=sup["brief"], help=sup["help"], aliases=sup["aliases"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def _support(self, ctx: commands.Context) -> None:
        link = community_support

        commands_counter.labels("support")
        commands_counter.labels("support").inc()

        try:
            channel = await ctx.author.create_dm()
            await channel.send(link)
            await ctx.defer(ephemeral=True)
            await ctx.send("Link already in your direct messages 👋")
        except discord.Forbidden:
            # await ctx.defer(ephemeral=True) # without defer cos bot cant send it if blocked
            await ctx.send(f'**Forbidden**\n'
                           f'Bot does not have permissions to write you DM.')

    # ABOUT ERRORS HANDLER
    @_about.error
    async def _about_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("about", "BotMissingPermissions")
            errors_counter.labels("about", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')

    # FEEDBACK ERRORS HANDLER
    @_send_feedback.error
    async def _send_feedback_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("feedback", "BotMissingPermissions")
            errors_counter.labels("feedback", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')
        if isinstance(error, commands.BadArgument):
            errors_counter.labels("feedback", "BadArgument")
            errors_counter.labels("feedback", "BadArgument").inc()
            log_txt = "File exist already "
            logger(log_file, "ERROR", log_txt)
            await ctx.defer(ephemeral=True)
            await ctx.send(f'Something wrong on our end.')
        if isinstance(error, commands.MissingRequiredArgument):
            errors_counter.labels("feedback", "MissingRequiredArgument")
            errors_counter.labels("feedback", "MissingRequiredArgument").inc()
            prefix = ctx.prefix
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Missing Required Argument**\n'
                           f'You should to write feedback message.'
                           f'Try something like: ```{prefix}feedback Awesome bot!```')

    # HELLO ERRORS HANDLER
    @_hello.error
    async def _hello_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("hello", "BotMissingPermissions")
            errors_counter.labels("hello", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')

    # SUPPORT ERRORS HANDLER
    @_support.error
    async def _support_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("support", "BotMissingPermissions")
            errors_counter.labels("support", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Community(bot))
