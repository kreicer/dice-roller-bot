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
from models.limits import dice_limit
from models.postfixes import postfixes
from models.metrics import dice_edge_counter, edge_valid


def json_writer(new_data, filename):
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data["jokes"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)


def text_writer(text, directory):
    file_id = str(uuid.uuid4())
    filename = file_id + ".txt"
    filepath = directory + "/" + filename
    check_file_exist(filepath)
    with open(filepath, "w") as file:
        file.write(text)


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
        dice += i
        if i not in ["+", "-"]:
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
            output += f"{green_start}{postfix}{gray_start}{all_end}"
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
