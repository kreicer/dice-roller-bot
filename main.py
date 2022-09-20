# IMPORTS
import asyncio
import datetime
import discord
import random
import sqlite3
import re
import topgg

from table2ascii import table2ascii as t2a, Alignment
from discord.ext import commands, tasks
from config import settings, jokes_db, admin_db

# VARIABLES
# Change only the no_category default string
help_command = commands.DefaultHelpCommand(no_category='Commands', indent=3)

# set bot commands prefix and number of shards
bot_prefix = settings['prefix']
bot_shards = settings['shards']


# define prefix or mention
async def get_prefix(bot, message):
    # TODO: mb allow few prefixes for each guild
    prefix_list = []
    db = sqlite3.connect(admin_db)
    cur = db.cursor()
    guild_id = str(message.guild.id)
    prefix_sql = "SELECT guild_prefix FROM guild_prefixes WHERE guild_id = ?;"
    cur.execute(prefix_sql, [guild_id])
    guild_prefix = cur.fetchone()
    if guild_prefix is not None:
        guild_prefix = guild_prefix[0]
    else:
        guild_prefix = bot_prefix
    db.close()
    prefix_list.append(guild_prefix)
    return commands.when_mentioned_or(*prefix_list)(bot, message)


# customize bot with prefix and custom help
bot_client = commands.AutoShardedBot(command_prefix=get_prefix,
                                     help_command=help_command,
                                     shard_count=bot_shards)
# global var
guilds_number = 0
# commands short description list
cmd_brief = {
    "about": "Show info about the bot",
    "stat": "Show bot statistics",
    "hello": "Show welcome message",
    "joke": "Get a DnD joke",
    "roll": "Roll the dice",
    "mod": "Roll the dice with modifiers",
    "d": "Roll single die",
    "prefix": "Manage bot prefix (admin only)",
    "prefix_set": "Set new prefix for the bot commands",
    "prefix_restore": "Restore default prefix"
}

# commands long description list
cmd_help = {
    "about": "Show bot version, Privacy Policy, link on Github, link on top.gg etc",
    "stat": "Show number of shards, number of servers using it etc",
    "hello": "Dice Roller greetings you and tell a little about himself.",
    "joke": "Bot post a random DnD joke from database (soon you will get opportunity to add yours jokes).",
    "roll": f"Roll different type of dice in one roll:\n \
            - single die, single roll: d20\n \
            - single die, multiple rolls: 10d4\n \
            - multiple dice, single roll: d4 d8 d20\n \
            - multiple dice, multiple rolls: 4d8 4d4 2d20\n \
            - fate dice: fate dF 6dF\n \
            - exploding dice: explode Ed20\n \
            - co-co-combo: d20 5d10 fate d123 Ed8",
    "mod": f"Roll different type of dice with mods in one roll:\n \
            - single die, single roll: d20+1\n \
            - single die, multiple rolls: 10d4-2\n \
            - multiple dice, single roll: d4-1 d20+2 d100-10\n \
            - multiple dice, multiple roll: 5d4+1 2d20-2 4d6-1\n \
            - fate dice: fate 4dF+1 10dF-2\n \
            - exploding dice: explode Ed20-4 Ed6+1\n \
            - co-co-combo: d20 5d10-2 2d100 fate d123+5 Ed10-2",
    "d": f"Single roll of single type die: \n \
            - 20\n \
            - 8\n \
            - 100",
    "prefix": "Manage prefix for the bot commands",
    "prefix_set": "Set new prefix",
    "prefix_restore": "Restore default prefix"
}

# commands usage list
cmd_usage = {
    "roll": "dice_1 [dice_2 ... dice_n]",
    "mod": "dice_1 [dice_2 ... dice_n]"
}

cmd_alias = {
    "about": ["bot", "version"],
    "stat": ["s"],
    "hello": ["sup", "hi", "Hello"],
    "joke": ["j", "J", "Joke"],
    "roll": ["r", "R", "Roll"],
    "mod": ["m", "M", "Mod"],
    "d": ["D"],
    "prefix": ["p", "P"],
    "prefix_set": ["s"],
    "prefix_restore": ["r"]
}

suffix_verbs = ['pass']
mod_types = ['pass', 'add', 'sub']
spec_dice = {
    "fate": "4dF",
    "explode": "Ed6"
}

limits = {
    "dice": 20,
    "edge": 1000000000,
    "mod": 1000000000,
    "prefix": 3,
    "roll": 50
}

# top.gg integration
if settings['send_stat']:
    bot_client.topggpy = topgg.DBLClient(bot_client, settings['topgg'], autopost=True, post_shard_count=True)

# db part
# TODO: make log system more common (not just print command)
conn = sqlite3.connect(jokes_db)
cursor = conn.cursor()
sql = "SELECT COUNT(joke_id) FROM jokes;"
number_of_jokes = 1


# FUNCTIONS
# check int
def check_int(possibly_int):
    try:
        exactly_int = int(possibly_int)
    except ValueError:
        result = False
    else:
        return exactly_int
    if not result:
        raise commands.BadArgument


# override negative
def check_subzero(possibly_subzero):
    number = possibly_subzero
    if int(number) < 0:
        number = 0
    return number


# check zero and negative
def check_one(possibly_zero_or_less):
    if possibly_zero_or_less < 1:
        raise commands.BadArgument


# sad but we need limits
def check_limit(number, limit):
    if number > limit:
        raise commands.ArgumentParsingError


# split modded dice for dice and mod parts
def split_mod_dice(dice):
    dice_stats_list = re.split(r'([+-])', dice)
    list_len = len(dice_stats_list)
    if list_len == 3:
        dice_without_mod = dice_stats_list[0]
        mod_math = dice_stats_list[1]
        mod_amount = dice_stats_list[2]
        mod_amount = check_int(mod_amount)
        check_limit(mod_amount, limits["mod"])
    elif list_len == 1:
        dice_without_mod = dice_stats_list[0]
        mod_math = ''
        mod_amount = ''
    else:
        raise commands.ArgumentParsingError
    return dice_without_mod, mod_math, mod_amount


# split and check dice for rolls and edges
def ident_dice(dice):
    dice_type = 'simple'
    rolls_and_edges = dice.split('d')
    if len(rolls_and_edges) != 2:
        raise commands.BadArgument
    dice_rolls = rolls_and_edges[0]
    dice_edge = rolls_and_edges[1]
    if dice_rolls.lower() == 'e':
        dice_type = 'explode'
        dice_rolls = dice_rolls.upper()
    else:
        if dice_rolls == '':
            dice_rolls = 1
        dice_rolls = check_int(dice_rolls)
        check_one(dice_rolls)
        check_limit(dice_rolls, limits["roll"])
    if dice_edge.lower() == 'f':
        dice_type = 'fate'
        dice_edge = dice_edge.upper()
    else:
        dice_edge = check_int(dice_edge)
        check_one(dice_edge)
        check_limit(dice_edge, limits["edge"])
    return dice_rolls, dice_edge, dice_type


# roll dice
def dice_roll(rolls, edge):
    dice_roll_result = []
    for counts in range(1, rolls + 1):
        roll_result = random.randint(1, edge)
        dice_roll_result.append(roll_result)
    return dice_roll_result


# fate roll
def fate_roll(rolls):
    dice_roll_result = []
    for counts in range(1, rolls + 1):
        roll_result = random.choices(["+", ".", "-"])
        dice_roll_result += roll_result
    return dice_roll_result


def fate_result(dice_result):
    total_result = dice_result.count('+') - dice_result.count('-')
    return total_result


# explode roll
def explode_roll(edge):
    dice_roll_result = []
    check = edge
    while check == edge:
        roll_result = random.randint(1, edge)
        dice_roll_result.append(roll_result)
        check = roll_result
    return dice_roll_result


# summarize result
def calc_result(dice_result):
    total_result = sum(dice_result)
    return total_result


# mod rolls result
def add_mod_result(total_result, mod_amount):
    total_mod_result = total_result + mod_amount
    return total_mod_result


def sub_mod_result(total_result, mod_amount):
    total_mod_result = total_result - mod_amount
    total_mod_result = check_subzero(total_mod_result)
    return total_mod_result


# create row for table output
def create_row(*args):
    table_row = []
    for item in args:
        table_row.append(item)
    return table_row


# create table from rows
def create_table(table_body):
    if len(table_body[0]) == 3:
        table_header = create_row('dice', 'rolls', 'sum')
    else:
        table_header = create_row('dice', 'result')
    columns = len(table_header) - 1
    output = t2a(
        header=table_header,
        body=table_body,
        first_col_heading=True,
        alignments=[Alignment.LEFT] + [Alignment.CENTER] * columns
    )
    return output


# add [] around sum number
def make_pretty_sum(not_so_pretty):
    pretty_sum = '[' + str(not_so_pretty) + ']'
    return pretty_sum


# make string from list for pretty rolls output
def make_pretty_rolls(not_so_pretty):
    delimiter = ' '
    size = 9
    pretty_rolls = ''
    if len(not_so_pretty) > size:
        batch_rolls = make_batch(not_so_pretty, size)
        for batch in batch_rolls:
            pretty_rolls += delimiter.join(str(r) for r in batch)
            pretty_rolls += '\n'
    else:
        pretty_rolls = delimiter.join(str(x) for x in not_so_pretty)
    return pretty_rolls


# let split longs for shorts
def make_batch(origin_list, size):
    new_list = []
    for i in range(0, len(origin_list), size):
        new_list.append(origin_list[i:i + size])
    return new_list


# return mod type for mod math actions
def add_or_sub(symbol):
    x = symbol
    if x == '+':
        mod_type = 'add'
        return mod_type
    elif x == '-':
        mod_type = 'sub'
        return mod_type
    else:
        mod_type = 'pass'
        return mod_type


# make dice label for table from args
def dice_maker(*args):
    result = ''
    for arg in args:
        result += str(arg)
    return result


# get prefix
def prefix_for_help(message):
    guild_id = str(message.guild.id)
    db = sqlite3.connect(admin_db)
    cur = db.cursor()
    prefix_sql = "SELECT guild_prefix FROM guild_prefixes WHERE guild_id = ?;"
    cur.execute(prefix_sql, [guild_id])
    guild_prefix = cur.fetchone()
    if guild_prefix is not None:
        guild_prefix = guild_prefix[0]
    else:
        guild_prefix = bot_prefix
    db.close()
    return guild_prefix


# EVENTS
# on connect actions
@bot_client.event
async def on_connect():
    # log connection info
    print(datetime.datetime.now(), 'INFO', 'Bot connected')


# on ready actions
@bot_client.event
async def on_ready():
    # log ready info
    print(datetime.datetime.now(), 'INFO', 'Bot ready')
    # log connected guilds number
    print(datetime.datetime.now(), 'INFO', 'Number of servers connected to:', len(bot_client.guilds))
    await bot_client.change_presence(activity=discord.Activity(name='dice rolling!',
                                                               type=discord.ActivityType.competing))
    await asyncio.sleep(10)
    # start number of jokes update loop
    update_jokes.start()
    await asyncio.sleep(10)
    # start status update loop
    update_guild_number.start()


# wrong commands handler
@bot_client.event
async def on_command_error(ctx, error):
    author = ctx.message.author
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'{author.mention}, command not found.\n'
                       f'Please, use the "{bot_prefix}help" command to get full list of commands.')


# top.gg successful post event
@bot_client.event
async def on_autopost_success():
    print(datetime.datetime.now(), 'INFO', 'Posted server count on Top.gg')


# remove prefix from Admin DB when bot was kicked from server
@bot_client.event
async def on_guild_remove(guild):
    guild_id = guild.id
    secure_guild_id = (guild_id,)
    prefix_sql = "DELETE FROM guild_prefixes WHERE guild_id=?;"
    db = sqlite3.connect(admin_db)
    cur = db.cursor()
    cur.execute(prefix_sql, secure_guild_id)
    db.commit()
    db.close()
    print(datetime.datetime.now(), 'INFO', 'Dice Roller was kicked from guild with id:', guild_id)


# LOOPS
# status update loop
@tasks.loop(hours=1)
async def update_guild_number():
    print(datetime.datetime.now(), 'INFO', 'Bot status updated, current number:', len(bot_client.guilds))
    global guilds_number
    guilds_number = len(bot_client.guilds)


# number of jokes update loop
@tasks.loop(hours=1)
async def update_jokes():
    cursor.execute(sql)
    global number_of_jokes
    number_of_jokes = cursor.fetchone()[0]
    print(datetime.datetime.now(), 'INFO', 'Jokes number updated, current number:', number_of_jokes)
    return number_of_jokes


# ADMIN COMMANDS AND ERRORS HANDLERS
# PREFIX GROUP
@bot_client.group(brief=cmd_brief["prefix"], help=cmd_help["prefix"], aliases=cmd_alias["prefix"],
                  invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def prefix(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f'```Invalid subcommand passed. Use:\n'
                       f'- set: to set new prefix\n'
                       f'- restore: to restore default prefix```')


# PREFIX SET COMMAND
@prefix.command(name='set', brief=cmd_brief["prefix_set"], help=cmd_help["prefix_set"], aliases=cmd_alias["prefix_set"])
@commands.cooldown(1, 1, commands.BucketType.user)
@commands.has_permissions(administrator=True)
async def set_prefix(ctx, new_prefix):
    check_limit(len(new_prefix), limits["prefix"])
    guild_id = str(ctx.guild.id)
    secure_prefix = tuple((guild_id, str(new_prefix)))
    prefix_sql = "INSERT OR REPLACE INTO guild_prefixes (guild_id, guild_prefix) VALUES (?,?);"
    db = sqlite3.connect(admin_db)
    cur = db.cursor()
    cur.execute(prefix_sql, secure_prefix)
    db.commit()
    db.close()
    await ctx.send(f'```New prefix is: {new_prefix}```')


# PREFIX RESTORE COMMAND
@prefix.command(name='restore', brief=cmd_brief["prefix_restore"], help=cmd_help["prefix_restore"],
                aliases=cmd_alias["prefix_restore"])
@commands.has_permissions(administrator=True)
async def restore_prefix(ctx):
    guild_id = str(ctx.guild.id)
    secure_guild_id = (guild_id,)
    prefix_sql = "DELETE FROM guild_prefixes WHERE guild_id=?;"
    db = sqlite3.connect(admin_db)
    cur = db.cursor()
    cur.execute(prefix_sql, secure_guild_id)
    db.commit()
    db.close()
    await ctx.send(f'```Prefix was restored to default value: {bot_prefix}```')


# PREFIX SET ERRORS HANDLER
@set_prefix.error
async def prefix_error(ctx, error):
    author = ctx.message.author
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{author.mention}, sorry, but you need administrator permissions to change the bot prefix.')
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{author.mention}, specify valid prefix, please.\n'
                       'Empty prefix specified.')
    if isinstance(error, commands.ArgumentParsingError):
        await ctx.send(f'{author.mention}, specify valid prefix, please.\n'
                       f'Specified prefix is longer than {limits["prefix"]} symbols.')
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'{author.mention}, this command is on cooldown.\n'
                       f'You can use it in {round(error.retry_after, 2)} sec.')


# USER COMMANDS AND ERRORS HANDLERS
# JOKE COMMAND
@bot_client.command(brief=cmd_brief["joke"], help=cmd_help["joke"], aliases=cmd_alias["joke"])
async def joke(ctx):
    random_joke_number = random.randint(1, number_of_jokes)
    sql_joke = "SELECT joke_text FROM jokes WHERE joke_id=?;"
    cursor.execute(sql_joke, [random_joke_number])
    joke_text = cursor.fetchone()[0]
    await ctx.send('Today joke is:\n' + joke_text)


# D COMMAND
@bot_client.command(brief=cmd_brief["d"], help=cmd_help["d"], aliases=cmd_alias["d"])
async def d(ctx, dice_edge):
    # prepare empty list for future output lines storing
    output_body = []
    # always single roll for d command
    rolls = 1
    # necessary checks: should be int, 1 or more and less than limit for edges
    edge = check_int(dice_edge)
    check_one(edge)
    check_limit(edge, limits["edge"])
    # roll
    roll_result = dice_roll(rolls, edge)
    # prepare dice for output
    output_dice = dice_maker('d', edge)
    # convert roll into list
    output_roll_result = make_pretty_rolls(roll_result)
    # create row for output
    table_row = create_row(output_dice, output_roll_result)
    # append rows
    output_body.append(table_row)
    # create table
    output = create_table(output_body)
    # send it into chat
    await ctx.send(f"```{output}```")


# D ERRORS HANDLER
@d.error
async def d_error(ctx, error):
    author = ctx.message.author
    help_prefix = prefix_for_help(ctx.message)
    if isinstance(error, commands.BadArgument):
        await ctx.send(f'{author.mention}, wrong dice edge.\n'
                       f'Try something like: ```{help_prefix}d 100```')
    if isinstance(error, commands.ArgumentParsingError):
        await ctx.send(f'{author.mention}, specify valid dice edge, please.\n'
                       f'Try something less than {limits["edge"]}.')
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{author.mention}, specify valid dice edge, please.\n'
                       f'Try something like: ```{help_prefix}d 20```')


# ROLL COMMAND
@bot_client.command(brief=cmd_brief["roll"], help=cmd_help["roll"], usage=cmd_usage["roll"], aliases=cmd_alias["roll"])
async def roll(ctx, *arg):
    all_dice = list(arg)
    dice_number = len(all_dice)
    if dice_number == 0:
        author = ctx.message.author
        help_prefix = prefix_for_help(ctx.message)
        await ctx.send(f'{author.mention}, specify valid dice, please.\n'
                       f'Try something like: ```{help_prefix}roll 4d20```')
    check_limit(dice_number, limits["dice"])
    table_body = []

    for dice in all_dice:
        if dice in spec_dice:
            dice = spec_dice[dice]

        # let split our dice roll into number of dices and number of edges
        # 2d20: 2 - number of dices, 20 - number of edges, d - separator
        dice_rolls, dice_edge, dice_type = ident_dice(dice)
        if dice_type == 'simple':
            dice_roll_result = dice_roll(dice_rolls, dice_edge)
            result = calc_result(dice_roll_result)
        elif dice_type == 'fate':
            dice_roll_result = fate_roll(dice_rolls)
            result = fate_result(dice_roll_result)
        else:
            dice_roll_result = explode_roll(dice_edge)
            result = calc_result(dice_roll_result)

        table_dice = dice_maker(dice_rolls, 'd', dice_edge)
        table_dice_roll_result = make_pretty_rolls(dice_roll_result)
        table_result = make_pretty_sum(result)

        table_row = create_row(table_dice, table_dice_roll_result, table_result)
        table_body.append(table_row)

    output = create_table(table_body)
    # send it into chat
    await ctx.send(f"```{output}```")


# ROLL ERRORS HANDLER
@roll.error
async def roll_error(ctx, error):
    author = ctx.message.author
    help_prefix = prefix_for_help(ctx.message)
    if isinstance(error, commands.BadArgument):
        await ctx.send(f'{author.mention}, wrong dice.\n'
                       f'Try something like: ```{help_prefix}roll d20 5d4 3d10```')
    if isinstance(error, commands.ArgumentParsingError):
        await ctx.send(f'{author.mention}, specify valid dice parameters, please.\n'
                       f'```Current limits:\n'
                       f'- max dice number is {limits["dice"]}\n'
                       f'- max rolls per dice is {limits["roll"]}\n'
                       f'- max dice edge is {limits["edge"]}```')
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{author.mention}, specify valid dice, please.\n'
                       f'Try something like: ```{help_prefix}roll 4d20```')


# MOD COMMAND
@bot_client.command(brief=cmd_brief["mod"], help=cmd_help["mod"], usage=cmd_usage["mod"], aliases=cmd_alias["mod"])
async def mod(ctx, *arg):
    all_dice = list(arg)
    dice_number = len(all_dice)
    if dice_number == 0:
        author = ctx.message.author
        help_prefix = prefix_for_help(ctx.message)
        await ctx.send(f'{author.mention}, specify valid dice, please.\n'
                       f'Try something like: ```{help_prefix}mod 2d8+1```')
    check_limit(dice_number, limits["dice"])
    table_body = []

    for dice in all_dice:
        if dice in spec_dice:
            dice = spec_dice[dice]

        dice_raw, mod_math, mod_amount = split_mod_dice(dice)
        dice_rolls, dice_edge, dice_type = ident_dice(dice_raw)

        if dice_type == 'simple':
            dice_roll_result = dice_roll(dice_rolls, dice_edge)
            result = calc_result(dice_roll_result)
        elif dice_type == 'fate':
            dice_roll_result = fate_roll(dice_rolls)
            result = fate_result(dice_roll_result)
        else:
            dice_roll_result = explode_roll(dice_edge)
            result = calc_result(dice_roll_result)

        mod_type = add_or_sub(mod_math)

        if mod_type == 'add':
            result = add_mod_result(result, mod_amount)
        elif mod_type == 'sub':
            result = sub_mod_result(result, mod_amount)

        table_dice = dice_maker(dice_rolls, 'd', dice_edge, mod_math, mod_amount)
        table_dice_roll_result = make_pretty_rolls(dice_roll_result)
        table_result = make_pretty_sum(result)

        table_row = create_row(table_dice, table_dice_roll_result, table_result)
        table_body.append(table_row)

    output = create_table(table_body)
    # send it into chat
    await ctx.send(f"```{output}```")


# ROLL ERRORS HANDLER
@mod.error
async def mod_error(ctx, error):
    author = ctx.message.author
    help_prefix = prefix_for_help(ctx.message)
    if isinstance(error, commands.BadArgument):
        await ctx.send(f'{author.mention}, wrong dice.\n'
                       f'Try something like: ```{help_prefix}mod 3d10 d10-1 3d8+1 d100-10```')
    if isinstance(error, commands.ArgumentParsingError):
        await ctx.send(f'{author.mention}, specify valid dice parameters, please.\n'
                       f'```Current limits:\n'
                       f'- max dice number is {limits["dice"]}\n'
                       f'- max rolls per dice is {limits["roll"]}\n'
                       f'- max dice edge is {limits["edge"]}\n'
                       f'- max modifier is {limits["mod"]}```')
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{author.mention}, specify valid dice, please.\n'
                       f'Try something like: ```{help_prefix}mod 2d8+1```')


# HELLO COMMAND
@bot_client.command(brief=cmd_brief["hello"], help=cmd_help["hello"], aliases=cmd_alias["hello"])
async def hello(ctx):
    author = ctx.message.author
    help_prefix = prefix_for_help(ctx.message)
    await ctx.send(f'Hello, {author.mention}.\n'
                   f'My name is Dice Roller. '
                   f'I am here to help you with rolling dice. '
                   f'Please, ask "{help_prefix}help" to list commands with short description. '
                   f'Also, ask "{help_prefix}help <command_name>" for more info about each command and examples.')


# ABOUT COMMAND
@bot_client.command(brief=cmd_brief["about"], help=cmd_help["about"], aliases=cmd_alias["about"])
async def about(ctx):
    await ctx.send(f'```Version: 1.1.0\n'
                   f'Author: kreicer\n'
                   f'Github: https://bit.ly/dice_roller_github\n'
                   f'Top.gg: https://bit.ly/dice_roller_vote\n'
                   f'Support Us: https://bit.ly/dice_roller_support\n'
                   f'Privacy Policy: https://bit.ly/dice_roller_privacy```')


# STAT COMMAND
@bot_client.command(brief=cmd_brief["stat"], help=cmd_help["stat"], aliases=cmd_alias["stat"])
async def stat(ctx):
    await ctx.send(f'```Statistics:\n'
                   f'Shards: {bot_shards}\n'
                   f'Servers: {guilds_number}```')


# bot start
bot_client.run(settings['token'])

# close sqlite connection
conn.close()
