import sqlite3
import configparser
import random
from discord.ext import commands, tasks
from models.commands import joke as j, joke_hear as j_hear, joke_tell as j_tell
from models.limits import joke_limit
from functions.checks import check_limit, check_lang
from functions.workhorses import text_writer, logger
from lang.list import available_languages as lang_list

# get params from config
config = configparser.ConfigParser()
config.read_file(open("config"))
jokes_db = config.get("db", "jokes_db")
log_file = config.get("logs", "log_file")

# global
number_of_jokes = 1


# for higher versions
# class Buttons(discord.ui.View):
#    def __init__(self, ctx):
#        super().__init__(timeout=None)
#        self.ctx = ctx
#
#    @discord.ui.button(label="Use This", style=discord.ButtonStyle.blurple)
#    async def use_this_button(self, button: discord.ui.Button, interaction: discord.Interaction):
#        await interaction.response.pong
#        await self.ctx.send('Hello!')
#
#    @discord.ui.button(label="Dismiss", style=discord.ButtonStyle.gray)
#    async def dismiss_button(self, button: discord.ui.Button, interaction: discord.Interaction):
#        await interaction.command.joke
#        await self.ctx.delete()


# jokes cog
class Jokes(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self._update_jokes.add_exception_type(sqlite3.OperationalError)
        self._update_jokes.start()

    def cog_unload(self):
        self._update_jokes.cancel()

    @tasks.loop(hours=1)
    async def _update_jokes(self):
        global number_of_jokes
        sql = "SELECT COUNT(joke_id) FROM jokes;"
        try:
            db = sqlite3.connect(jokes_db)
            cur = db.cursor()
            cur.execute(sql)
            number_of_jokes = cur.fetchone()[0]
            db.close()
            # Logger
            log_txt = "Jokes number updated, current number: " + str(number_of_jokes)
            logger(log_file, "INFO", log_txt)
        except sqlite3.OperationalError:
            log_txt = f"Failed to load database file - {jokes_db}"
            logger(log_file, "ERROR", log_txt)
        return number_of_jokes

    @commands.hybrid_group(name=j["name"], brief=j["brief"], help=j["help"], aliases=j["aliases"],
                           invoke_without_command=True, with_app_command=True)
    async def _joke(self, ctx: commands.Context) -> None:
        prefix = ctx.prefix
        if ctx.invoked_subcommand is None:
            await ctx.defer(ephemeral=True)
            await ctx.send(f'Please choose: you want to tell joke or hear it.'
                           f'```{prefix}joke tell```'
                           f'```{prefix}joke hear```')

    @_joke.command(name=j_hear["name"], brief=j_hear["brief"], usage=j_hear["usage"], help=j_hear["help"],
                   with_app_command=True)
    async def _joke_hear(self, ctx: commands.Context,
                         everyone: bool = commands.parameter(default=True,
                                                             displayed_default="Yes",
                                                             description="Send to channel")) -> None:
        random_joke_number = random.randint(1, number_of_jokes)
        db = sqlite3.connect(jokes_db)
        cur = db.cursor()
        sql_joke = "SELECT joke_text FROM jokes WHERE joke_id=?;"
        cur.execute(sql_joke, [random_joke_number])
        joke_text = cur.fetchone()[0]
        db.close()
        if not everyone:
            await ctx.defer(ephemeral=True)
        await ctx.send(f'Today joke is: ```{joke_text}```')

    @_joke.command(name=j_tell["name"], brief=j_tell["brief"], help=j_tell["help"], usage=j_tell["usage"],
                   with_app_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _joke_tell(self, ctx: commands.Context,
                         language: str = commands.parameter(description="Language of joke"),
                         joke: str = commands.parameter(description="Text of joke")) -> None:
        joke_len = len(joke)
        for_error = {
            "lang": language,
            "joke": joke
        }
        language = language.upper()
        check_lang(language, for_error)
        check_limit(joke_len, joke_limit, for_error)
        author = ctx.message.author
        directory = "jokes"
        joke = "\"" + joke + "\""
        text_writer(joke, directory)
        # Logger
        log_txt = "New joke was posted by " + str(author)
        logger(log_file, "INFO", log_txt)
        # Output
        await ctx.defer(ephemeral=True)
        await ctx.send(f'Your joke is accepted! ```Language of joke: {language}\nJoke text: {joke}```')

    # JOKE ERRORS HANDLER
    @_joke.error
    async def _joke_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.defer(ephemeral=True)
            await ctx.send(f'Dice Roller have missing permissions to answer you in this channel.\n'
                           f'You can solve it by adding rights in channel or server management section.')

    # JOKE TELL ERRORS HANDLER
    @_joke_tell.error
    async def _joke_tell_error(self, ctx, error):
        prefix = ctx.prefix
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Bot Missing Permissions**\n'
                           f'Dice Roller have missing permissions to answer you in this channel.\n'
                           f'You can solve it by adding rights in channel or server management section.')
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Missing Required Argument**\n'
                           f'Specify valid arguments: language of joke and joke text, please. '
                           f'Example: ```{prefix}submit EN \"Joke text...\"```')
        if isinstance(error, commands.ArgumentParsingError):
            error_dict = error.args[0]
            joke_text = error_dict["joke"]
            lang = error_dict["lang"]
            shorter_joke = joke_text[:joke_limit - 2]
            joke_len = len(joke_text)
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Argument Parsing Error**\n'
                           f'Make your joke shorter, please.\n'
                           f'The submitted joke has length {joke_len} which is greater than the limit '
                           f'in {joke_limit} symbols. Example:'
                           f'```{prefix}joke tell {lang} \"{shorter_joke}\"```')
        if isinstance(error, commands.BadArgument):
            error_dict = error.args[0]
            joke_text = error_dict["joke"]
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Bad Argument**\n'
                           f'Chosen language not in list of available languages.\n'
                           f'Please, ensure you choose one of this languages {lang_list}. '
                           f'Or contact support server with add language request. Example:'
                           f'```{prefix}submit EN \"{joke_text}\"```')
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Command On Cooldown**\n'
                           f'This command is on cooldown.\n'
                           f'You can use it in {round(error.retry_after, 2)} sec.')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Jokes(bot))
