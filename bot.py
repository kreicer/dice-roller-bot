import discord
from discord.ext import commands

from functions.sql import select_sql, apply_sql
from models.metrics import guilds_counter
from functions.config import bot_version, bot_token, bot_prefix, bot_shards, db_admin, log_file
from functions.workhorses import logger
from models.sql import prefix_get, shortcut_delete_all, prefix_delete, source_delete, source_update, stat_delete, \
    custom_dice_delete_all
from ui.community import HelpView, PostfixView, ActionsView
from ui.jokes import JokesView
from ui.server import StatView, PrefixView, ConfirmView, SuccessView


# define prefix or mention
async def get_prefix(bot, message):
    prefix_list = []
    try:
        discord_id = str(message.guild.id)
    except AttributeError:
        discord_id = str(message.channel.id)
    secure = (discord_id,)
    guild_prefix = select_sql(db_admin, prefix_get, secure)
    if guild_prefix == "":
        guild_prefix = bot_prefix
    prefix_list.append(guild_prefix)
    return commands.when_mentioned_or(*prefix_list)(bot, message)


# customize bot with prefix and custom help
intents = discord.Intents.default()
intents.message_content = True


class RollerBot(commands.AutoShardedBot):
    def __init__(self) -> None:
        super().__init__(command_prefix=get_prefix,
                         help_command=None,
                         shard_count=bot_shards,
                         intents=intents)

    async def setup_hook(self) -> None:
        await roller.load_extension("cogs.server")
        await roller.load_extension("cogs.metrics")
        await roller.load_extension("cogs.integrations")
        await roller.load_extension("cogs.roll")
        await roller.load_extension("cogs.context")
        await roller.load_extension("cogs.jokes")
        await roller.load_extension("cogs.community")
        await self.tree.sync()


roller = RollerBot()


# EVENTS
# on connect actions
@roller.event
async def on_connect():
    # log connection info
    log_txt = "Bot connected"
    logger(log_file, "INFO", log_txt)


# on ready actions
@roller.event
async def on_ready():
    # log ready info and connected guilds number
    log_txt = "Bot ready and connected to " + str(len(roller.guilds)) + " servers"
    logger(log_file, "INFO", log_txt)
    roller.add_view(JokesView())
    roller.add_view(HelpView())
    roller.add_view(PostfixView())
    roller.add_view(ActionsView())
    roller.add_view(StatView())
    roller.add_view(PrefixView())
    roller.add_view(ConfirmView())
    roller.add_view(SuccessView())
    # roller.add_view(ShortcutView())
    await roller.change_presence(activity=discord.Activity(name=f'v{bot_version}!',
                                                           type=discord.ActivityType.competing))


# remove prefix from Admin DB when bot was kicked from server
@roller.event
async def on_guild_remove(guild):
    # main
    discord_id = str(guild.id)
    secure = (discord_id,)
    execute_list = [
        (shortcut_delete_all, secure),
        (custom_dice_delete_all, secure),
        (stat_delete, secure),
        (prefix_delete, secure),
        (source_delete, secure)
    ]
    apply_sql(db_admin, execute_list)

    # logger
    log_txt = f"Dice Roller was kicked from guild with id: {discord_id}"
    logger(log_file, "INFO", log_txt)

    # metrics
    guilds_counter.labels("kicked")
    guilds_counter.labels("kicked").inc()


@roller.event
async def on_guild_join(guild):
    # main
    discord_id = str(guild.id)
    secure = (discord_id,)
    execute_list = [(source_update, secure)]
    apply_sql(db_admin, execute_list)

    # logger
    log_txt = f"Dice Roller was added on guild with id: {discord_id}"
    logger(log_file, "INFO", log_txt)

    # metrics
    guilds_counter.labels("joined")
    guilds_counter.labels("joined").inc()


# wrong commands handler
@roller.event
async def on_command_error(ctx, error):
    prefix = ctx.prefix
    if isinstance(error, commands.CommandNotFound):
        try:
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Command Not Found**\n'
                           f'Use the "{prefix}help" command to get full list of commands')
        except discord.Forbidden:
            dm = await ctx.author.create_dm()
            await dm.send(f'**Forbidden**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')


roller.run(bot_token)
