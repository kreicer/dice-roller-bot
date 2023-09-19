import sqlite3
import discord
from discord.ext import commands
from models.metrics import guilds_counter
from functions.config import bot_version, bot_token, bot_prefix, bot_shards, db_admin, log_file
from functions.workhorses import logger


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
                         help_command=None,
                         shard_count=bot_shards,
                         intents=intents)

    async def setup_hook(self) -> None:
        await roller.load_extension("cogs.root")
        await roller.load_extension("cogs.server")
        await roller.load_extension("cogs.roll")
        await roller.load_extension("cogs.jokes")
        await roller.load_extension("cogs.community")
        await roller.load_extension("cogs.integrations")
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
    discord_id = guild.id
    secure_args = (discord_id,)
    prefix_sql = "DELETE FROM prefix WHERE discord_id=?;"
    shortcut_sql = "DELETE FROM shortcut WHERE discord_id=?;"
    source_sql = "DELETE FROM source WHERE discord_id=?;"
    try:
        db = sqlite3.connect(db_admin)
        cur = db.cursor()
        cur.execute(prefix_sql, secure_args)
        cur.execute(shortcut_sql, secure_args)
        cur.execute(source_sql, secure_args)
        db.commit()
        db.close()
        log_txt = f"Dice Roller was kicked from guild with id: {discord_id}"
        logger(log_file, "INFO", log_txt)
    except sqlite3.OperationalError:
        log_txt = f"Failed to load database file - {db_admin}"
        logger(log_file, "ERROR", log_txt)
    # metrics
    guilds_counter.labels("kicked")
    guilds_counter.labels("kicked").inc()


@roller.event
async def on_guild_join(guild):
    discord_id = str(guild.id)
    source_type = 1
    source_args = tuple((discord_id, source_type))
    source_sql = "INSERT OR REPLACE INTO source (discord_id, type) VALUES (?,?);"
    try:
        db = sqlite3.connect(db_admin)
        cur = db.cursor()
        cur.execute(source_sql, source_args)
        db.commit()
        db.close()
        log_txt = f"Dice Roller was added on guild with id: {discord_id}"
        logger(log_file, "INFO", log_txt)
    except sqlite3.OperationalError:
        log_txt = f"Failed to load database file - {db_admin}"
        logger(log_file, "ERROR", log_txt)
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
