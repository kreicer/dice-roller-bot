import json
import re
import sqlite3
import uuid
import datetime
import random
from functions.checks import (
    check_match,
    check_dice_dict,
    check_file_exist,
    check_limit
)
from functions.config import db_admin
from functions.sql import select_sql
from lang.EN.errors import bucket_error

from models.limits import dice_limit
from models.metrics import dice_edge_counter, edge_valid
from models.sql import shortcut_get_dice


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


def split_dice_actions(bucket):
    split_list = bucket.split("|")
    cleared_bucket = split_list[0]
    split_list.pop(0)
    actions = split_list
    return cleared_bucket, actions


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
    error_text = bucket_error.format(len_for_check, dice_limit)
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
    dice_edge_counter.labels("all")
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


def check_if_shortcut(discord_id, bucket):
    try:
        result = select_sql(db_admin, shortcut_get_dice, (discord_id, bucket))
    except sqlite3.OperationalError:
        return bucket
    if result:
        return result
    else:
        return bucket
