# module and files import section
import discord
import random
import sqlite3
from discord.ext import commands, tasks
from config import settings, dbname

# set bot commands prefix
bot = commands.Bot(command_prefix=settings['prefix'])
conn = sqlite3.connect(dbname)
cursor = conn.cursor()
sql = "SELECT COUNT(joke_id) FROM jokes;"
cursor.execute(sql)
number_of_jokes = cursor.fetchone()[0]


# hello command, lets introduce our bot and functions
@bot.command()
async def hello(ctx):
    """
    Basic information
    """

    author = ctx.message.author
    await ctx.send(f'Hello, {author.mention}.\n'
                   f'My name is Dice Roller. '
                   f'I am here to help you with rolling dices. '
                   f'Please, ask "?help" for more info about commands.')


# wrong commands handler
@bot.event
async def on_command_error(ctx, error):
    author = ctx.message.author
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'{author.mention}, команда не найдена.\n'
                       f'Используйте команду "?help", чтобы узнать список команд.')


# joke command, it should post random DnD or another role-play game joke
# TODO: use sql instead of simple list
@bot.command()
async def joke(ctx):
    """
    Get a joke
    """

    random_joke_number = random.randint(1, number_of_jokes)
    sql_joke = "SELECT joke_text FROM jokes WHERE joke_id=?;"
    cursor.execute(sql_joke, [random_joke_number])
    joke_text = cursor.fetchone()[0]
    await ctx.send('Today joke is:\n' + joke_text)


# command for rolling dices
# TODO: add more checks, optimize current checks
@bot.command()
async def roll(ctx, *arg):
    """
    Roll the dices
    """

    # get rolls list from text after bot command
    rolls = list(arg)
    # start our result from empty string
    result = ''

    # for each roll do some checks and preparations
    for dice_roll in rolls:
        # lets split our dice roll into number of dices and number of edges
        # 2d20: 2 - number of dices, 20 - number of edges, d - separator
        # TODO: maybe better create class for dices?
        numbers = dice_roll.split('d')

        # convert '' into number of dices, count as 1, ex: d20 == 1d20
        dice_count = numbers[0]
        if dice_count == '':
            dice_count = '1'

        # check on number of edges is exist
        try:
            dice_edge = numbers[1]
        except Exception:
            raise commands.BadArgument

        # check on count of separated parts to fix constructions like 2d20d20
        if len(numbers) != 2:
            raise commands.BadArgument

        # check on dice count and edges can be converted into integer
        try:
            int(dice_count)
            int(dice_edge)
        except Exception:
            raise commands.BadArgument

        # if dice count or edge less than 1 then ignore this roll
        if int(dice_count) < 1 or int(dice_edge) < 1:
            continue

        # if roll should be done lets add text section for it
        result += '\nD' + dice_edge + ':'

        # roll each dice of current edge
        for counts in range(1, int(dice_count) + 1):
            # get result of current roll dice and convert into string
            sub_result = str(random.randint(1, int(dice_edge)))
            # add sub result with some formatting into result
            result += '  **' + sub_result + '**'

    # create embed object from result for discord chat
    embed = discord.Embed(color=0xff0000, title=result)
    # send it into chat
    await ctx.send(embed=embed)


# bad argument exception
@roll.error
async def roll_error(ctx, error):
    author = ctx.message.author
    if isinstance(error, commands.BadArgument):
        await ctx.send(f'{author.mention}, неправильный кубик.\n'
                       f'Попробуйте задать один или несколько кубов в формате "кол-во"d"грани".\n'
                       f'Количество указывается целым числом или не указывается для одного кубика.\n'
                       f'Грани указываются любым целым числом больше нуля.\n'
                       f'Пример: 2d20 d100 6d4')

bot.run(settings['token'])

# close sqlite connection
conn.close()
