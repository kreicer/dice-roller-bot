import sqlite3
import discord
from discord.ext import commands
from models.metrics import guilds_counter
from functions.config import bot_version, bot_token, bot_prefix, bot_shards, db_admin, log_file
from functions.workhorses import logger

# Change only the no_category default string
help_command = commands.DefaultHelpCommand(no_category='Help', indent=3)


# define prefix or mention
async def get_prefix(bot, message):
    # TODO: mb allow few prefixes for each guild
    prefix_list = []
    try:
        db = sqlite3.connect(db_admin)
        cur = db.cursor()
        try:
            guild_id = str(message.guild.id)
        except AttributeError:
            guild_id = str(message.channel.id)
        prefix_sql = "SELECT guild_prefix FROM guild_prefixes WHERE guild_id = ?;"
        cur.execute(prefix_sql, [guild_id])
        guild_prefix = cur.fetchone()
        if guild_prefix is not None:
            guild_prefix = guild_prefix[0]
        else:
            guild_prefix = bot_prefix
        db.close()
    except sqlite3.OperationalError:
        log_txt = f"Failed to load database file - {db_admin}"
        logger(log_file, "ERROR", log_txt)
        guild_prefix = bot_prefix
    prefix_list.append(guild_prefix)
    return commands.when_mentioned_or(*prefix_list)(bot, message)


# customize bot with prefix and custom help
intents = discord.Intents.default()
intents.message_content = True


class RollerBot(commands.AutoShardedBot):
    def __init__(self) -> None:
        super().__init__(command_prefix=get_prefix,
                         help_command=help_command,
                         shard_count=bot_shards,
                         intents=intents)

    async def setup_hook(self) -> None:
        await roller.load_extension("cogs.root")
        await roller.load_extension("cogs.admin")
        await roller.load_extension("cogs.roll")
        await roller.load_extension("cogs.jokes")
        await roller.load_extension("cogs.community")
        await roller.load_extension("cogs.integrations")
        await roller.load_extension("cogs.info")
        await roller.load_extension("cogs.metrics")
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
    await roller.change_presence(activity=discord.Activity(name=f'v{bot_version}!',
                                                           type=discord.ActivityType.competing))


# remove prefix from Admin DB when bot was kicked from server
@roller.event
async def on_guild_remove(guild):
    guild_id = guild.id
    secure_guild_id = (guild_id,)
    prefix_sql = "DELETE FROM guild_prefixes WHERE guild_id=?;"
    try:
        db = sqlite3.connect(db_admin)
        cur = db.cursor()
        cur.execute(prefix_sql, secure_guild_id)
        db.commit()
        db.close()
        log_txt = f"Dice Roller was kicked from guild with id: {guild_id}"
        logger(log_file, "INFO", log_txt)
    except sqlite3.OperationalError:
        log_txt = f"Failed to load database file - {db_admin}"
        logger(log_file, "ERROR", log_txt)
    guilds_counter.labels("kicked")
    guilds_counter.labels("kicked").inc()


@roller.event
async def on_guild_join(guild):
    guilds_counter.labels("joined")
    guilds_counter.labels("joined").inc()


# wrong commands handler
@roller.event
async def on_command_error(ctx, error):
    prefix = ctx.prefix
    if isinstance(error, commands.CommandNotFound):
        await ctx.defer(ephemeral=True)
        await ctx.send(f'**Command Not Found**\n'
                       f'Use the "{prefix}help" command to get full list of commands')


roller.run(bot_token)
