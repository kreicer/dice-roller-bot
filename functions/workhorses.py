import json
import re
import uuid
import datetime
import random
from functions.checks import (
    check_match,
    check_dice_dict,
    check_file_exist,
    check_limit,
    check_postfix_is_right_and_available
)
from functions.config import bot_name, bot_version, dev_name, bot_shards
from models.limits import dice_limit
from models.postfixes import postfixes
from models.commands import cmds
from models.metrics import dice_edge_counter, edge_valid


def json_writer(new_data, filename):
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data["jokes"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)


def text_writer(text, directory):
    file_id = uuid_generator()
    filename = file_id + ".txt"
    filepath = directory + "/" + filename
    check_file_exist(filepath)
    with open(filepath, "w") as file:
        file.write(text)


def uuid_generator():
    new_uuid = str(uuid.uuid4())
    return new_uuid


def logger(filename, log_level, text):
    with open(filename, 'a') as file:
        print(datetime.datetime.now(), log_level, text, file=file)
    file.close()


def generate_dicts(dict_for_aliases):
    aliases = {}
    for key in dict_for_aliases.keys():
        for alias in dict_for_aliases[key]["aliases"]:
            aliases[alias] = key
    return aliases


def split_on_parts(dice, parsing_regexp):
    match = re.fullmatch(parsing_regexp, dice)
    check_match(match)
    dice_dict = match.groupdict()
    check_dice_dict(dice_dict)
    return dice_dict


def split_on_dice(bucket):
    dice_split_args = re.split(r'([+-])', bucket)
    str_list = list(filter(None, dice_split_args))
    list_of_dice = []
    dice = ""
    for i in str_list:
        if i in ["+", "-"]:
            dice += i
        else:
            dice += i
            list_of_dice.append(dice)
            dice = ""
    len_for_check = len(list_of_dice)
    error_text = f"Number of elements of the modified dice ({len_for_check}) " \
                 f"is greater than the current limit of {dice_limit}"
    check_limit(len_for_check, dice_limit, error_text)
    return list_of_dice


def dice_roll(throws, edge):
    dice_roll_result = []
    for counts in range(1, throws + 1):
        roll_result = random.randint(1, edge)
        dice_roll_result.append(roll_result)
    if edge in edge_valid:
        dice_edge_counter.labels(edge)
        dice_edge_counter.labels(edge).inc(throws)
    dice_edge_counter.labels("all").inc(throws)
    return dice_roll_result


def fate_roll(throws):
    dice_roll_result = []
    for counts in range(1, throws + 1):
        roll_result = random.choice(["+", "-", "."])
        dice_roll_result.append(roll_result)
    dice_edge_counter.labels("F")
    dice_edge_counter.labels("F").inc(throws)
    dice_edge_counter.labels("all").inc(throws)
    return dice_roll_result


# summarize result
def calc_result(dice_result):
    total_result = sum(dice_result)
    return total_result


def fate_result(dice_result):
    total_result = dice_result.count("+") - dice_result.count("-")
    return total_result


# mod rolls result
def add_mod_result(total_result, mod_amount):
    total_mod_result = total_result + mod_amount
    return total_mod_result


def sub_mod_result(total_result, mod_amount):
    total_mod_result = total_result - mod_amount
    return total_mod_result


def generate_postfix_short_output():
    green_start = "[0;32m"
    gray_start = "[0;30m"
    all_end = "[0;0m"
    output = f"```ansi\n{green_start}POSTFIXES{all_end}\n\n"
    for postfix in postfixes:
        if postfixes[postfix]["enabled"]:
            output += "- "
            output += f"{green_start}{postfix}{all_end}"
            output += " - "
            output += f"{postfixes[postfix]['shorty']}\n"
    output += "\n\n"
    output += "Postfix position in dice structure\n"
    output += f"{gray_start}<throws>d<edge>/{green_start}<postfix>{gray_start}:<value>{all_end}\n\n"
    output += f"{gray_start}For detailed info about each postfix use selector below```"
    return output


def generate_postfix_help(postfix):
    check_postfix_is_right_and_available(postfix)
    green_start = "[0;32m"
    blue_start = "[0;34m"
    all_end = "[0;0m"
    default = postfixes[postfix]['default_value']
    if default == "":
        default = "max"
    output = f"```ansi\n{green_start}{postfixes[postfix]['name'].upper()}{all_end}\n\n"
    output += f"{postfixes[postfix]['description']}\n\n"
    output += f"Aliases: {blue_start}{postfixes[postfix]['aliases']}{all_end}\n"
    output += f"Example: {blue_start}/{postfixes[postfix]['example']}{all_end}\n"
    output += f"Default value: {blue_start}{default}{all_end}```"
    return output


def generate_joke_output(joke_id, joke_text):
    green_start = "[0;32m"
    all_end = "[0;0m"
    output = f"```ansi\n" \
             f"{green_start}Joke #{joke_id}{all_end}\n\n" \
             f"{joke_text}\n" \
             f"```"
    return output


def generate_prefix_output(prefix, text):
    green_start = "[0;32m"
    yellow_start = "[0;33m"
    blue_start = "[0;34m"
    all_end = "[0;0m"
    output = f"```ansi\n" \
             f"{green_start}PREFIX {yellow_start}(ADMIN ACTION){all_end}\n\n" \
             f"{text} - {blue_start}{prefix}{all_end}\n" \
             f"```"
    return output


def generate_info_output(guilds_number):
    green_start = "[0;32m"
    blue_start = "[0;34m"
    all_end = "[0;0m"
    output = f"```ansi\n" \
             f"{green_start}{bot_name} v{bot_version} by {dev_name}{all_end}\n\n" \
             f"Shards: {blue_start}{bot_shards}{all_end}\n" \
             f"Servers: {blue_start}{guilds_number}{all_end}\n" \
             f"```"
    return output


def generate_help_short_output(cogs_dict):
    green_start = "[0;32m"
    gray_start = "[0;30m"
    all_end = "[0;0m"
    output = f"```ansi\n{green_start}HELP{all_end}\n\n"
    for key, value in cogs_dict.items():
        output += f"{key}:\n"
        for cmd in value:
            output += f"  {green_start}{cmds[cmd]['name']: <10}{all_end}{cmds[cmd]['brief']}\n"
        output += f"\n"
    output += "\n"
    output += f"{gray_start}For detailed info about each command use selector below{all_end}```"
    return output


def generate_commands_help(command):
    green_start = "[0;32m"
    blue_start = "[0;34m"
    all_end = "[0;0m"
    output = f"```ansi\n{green_start}{cmds[command]['name'].upper()}{all_end}\n\n"
    output += f"{cmds[command]['help']}\n\n"
    output += f"Aliases: {blue_start}{cmds[command]['aliases']}{all_end}\n"
    output += f"Usage: {blue_start}/{cmds[command]['name']} {cmds[command]['usage']}{all_end}\n```"
    return output


def generate_hello_text():
    green = "[0;32m"
    blue = "[0;34m"
    end = "[0;0m"
    output = f"```ansi\n" \
             f"Hello, friend!\n\n" \
             f"My name is {blue}Dice Roller{end}. I will be your guide in this awesome adventure. " \
             f"First of all, my core functionality - roll any dice you can image. " \
             f"And be you useful helper on this way, of course. " \
             f"I recommend start from something simple... Make a {green}d20{end} dice roll!\n\n" \
             f"You can roll simple dice, complex dice with multipliers and also with Postfixes! " \
             f"Let me show you some examples...\n\n" \
             f"Your command should start from {green}slash (/){end}, local bot {green}prefix{end} " \
             f"or bot {green}mention{end}. " \
             f"Next part - command name. In our case it will be {green}\"roll\"{end} or just {green}\"r\"{end}. " \
             f"Yep, whitespace next. " \
             f"And from this moment only you decide what you want to roll. " \
             f"Dice may be simple like {green}2d20{end}  or complex like {green}3d8+d4-1{end}. " \
             f"Dice may contain {green}Postfix{end}. I will provide this as example - {green}4d8/dl:2{end}. " \
             f"Best part here - you can combine any dice and roll more than one dice per command. " \
             f"Like this - {green}/roll 3d6+d4 3d20/dh 2d20+2d4/dl:1-1{end}. " \
             f"You can get full available list with command {green}/postfix{end}." \
             f"```"
    return output
