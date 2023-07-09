import sqlite3
from discord.ext import commands
from models.commands import prefix as pfx, prefix_set as spfx, prefix_restore as rpfx
from models.limits import prefix_limit
from models.metrics import commands_counter, errors_counter
from functions.checks import check_limit
from functions.workhorses import logger
from functions.config import db_admin, dev_link, log_file


# ADMIN COG
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # PREFIX COMMANDS GROUP
    @commands.hybrid_group(name=pfx["name"], brief=pfx["brief"], help=pfx["help"], aliases=pfx["aliases"],
                           invoke_without_command=True, with_app_command=True)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _prefix(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            prefix = ctx.prefix

            commands_counter.labels("prefix")
            commands_counter.labels("prefix").inc()

            await ctx.defer(ephemeral=True)
            await ctx.send(f'Please choose: you want to set prefix or restore it.'
                           f'```{prefix}prefix set```'
                           f'```{prefix}prefix restore```')

    # PREFIX SET COMMAND
    @_prefix.command(name=spfx["name"], brief=spfx["brief"], help=spfx["help"], aliases=spfx["aliases"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _set_prefix(self, ctx: commands.Context,
                          prefix: str = commands.parameter(description="New prefix for your server")) -> None:
        check_limit(len(prefix), prefix_limit, prefix)
        guild_id = str(ctx.guild.id)
        secure_prefix = tuple((guild_id, str(prefix)))
        sql = "INSERT OR REPLACE INTO guild_prefixes (guild_id, guild_prefix) VALUES (?,?);"
        try:
            db = sqlite3.connect(db_admin)
            cur = db.cursor()
            cur.execute(sql, secure_prefix)
            db.commit()
            db.close()
            await ctx.defer(ephemeral=True)
            await ctx.send(f'New prefix is: {prefix}')
        except sqlite3.OperationalError:
            log_txt = f"Failed to load database file - {db_admin}"
            logger(log_file, "ERROR", log_txt)
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**SQL Operational Error**\n'
                           f'Looks like Admin Database currently unavailable.\n'
                           f'Please, report to [developer]({dev_link}).')

        commands_counter.labels("prefix_set")
        commands_counter.labels("prefix_set").inc()

    # PREFIX RESTORE COMMAND
    @_prefix.command(name=rpfx["name"], brief=rpfx["brief"], help=rpfx["help"], aliases=rpfx["aliases"])
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _restore_prefix(self, ctx: commands.Context) -> None:
        guild_id = str(ctx.guild.id)
        secure_guild_id = (guild_id,)
        sql = "DELETE FROM guild_prefixes WHERE guild_id=?;"
        try:
            db = sqlite3.connect(db_admin)
            cur = db.cursor()
            cur.execute(sql, secure_guild_id)
            db.commit()
            db.close()
            await ctx.defer(ephemeral=True)
            await ctx.send(f'Prefix was restored to default value')
        except sqlite3.OperationalError:
            log_txt = f"Failed to load database file - {db_admin}"
            logger(log_file, "ERROR", log_txt)
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**SQL Operational Error**\n'
                           f'Looks like Admin Database currently unavailable.\n'
                           f'Please, report to [developer]({dev_link}).')

        commands_counter.labels("prefix_restore")
        commands_counter.labels("prefix_restore").inc()

    # PREFIX ERRORS HANDLER
    @_prefix.error
    async def _prefix_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("prefix", "BotMissingPermissions")
            errors_counter.labels("prefix", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')

    # PREFIX RESTORE ERRORS HANDLER
    @_restore_prefix.error
    async def _restore_prefix_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("prefix_restore", "BotMissingPermissions")
            errors_counter.labels("prefix_restore", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')

    # PREFIX SET ERRORS HANDLER
    @_set_prefix.error
    async def _set_prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            errors_counter.labels("prefix_set", "MissingPermissions")
            errors_counter.labels("prefix_set", "MissingPermissions").inc()
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Missing Permissions**\n'
                           f'Sorry, but you need administrator permissions to change the bot prefix.')
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("prefix_set", "BotMissingPermissions")
            errors_counter.labels("prefix_set", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')
        if isinstance(error, commands.MissingRequiredArgument):
            errors_counter.labels("prefix_set", "MissingRequiredArgument")
            errors_counter.labels("prefix_set", "MissingRequiredArgument").inc()
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Missing Required Argument**\n'
                           f'Specify valid prefix, please.\n'
                           'Empty prefix specified.')
        if isinstance(error, commands.ArgumentParsingError):
            errors_counter.labels("prefix_set", "ArgumentParsingError")
            errors_counter.labels("prefix_set", "ArgumentParsingError").inc()
            prefix = ctx.prefix
            new_prefix = error.args[0]
            shorter_prefix = new_prefix[:prefix_limit]
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Argument Parsing Error**\n'
                           f'Specify valid prefix, please.\n'
                           f'Specified prefix is longer than {prefix_limit} symbols. Example:'
                           f'```{prefix}prefix set {shorter_prefix}```')
        if isinstance(error, commands.CommandOnCooldown):
            errors_counter.labels("prefix_set", "CommandOnCooldown")
            errors_counter.labels("prefix_set", "CommandOnCooldown").inc()
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Command On Cooldown**\n'
                           f'This command is on cooldown.\n'
                           f'You can use it in {round(error.retry_after, 2)} sec.')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
