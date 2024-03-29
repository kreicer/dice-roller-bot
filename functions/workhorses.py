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
from functions.sql import select_sql, select_all_sql, apply_sql
from lang.EN.errors import bucket_error

from models.limits import dice_limit
from models.metrics import dice_edge_counter, edge_valid
from models.sql.common import shortcut_get_dice, stat_insert, stat_update
from functions.config import db_admin, db_user
from models.sql.user import autocomplete_get_all, autocomplete_count, autocomplete_update, autocomplete_delete


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


def check_if_shortcut(discord_id, user_id, bucket):
    try:
        result_user = select_sql(db_user, shortcut_get_dice, (user_id, bucket))
        result_admin = select_sql(db_admin, shortcut_get_dice, (discord_id, bucket))
    except sqlite3.OperationalError:
        return bucket
    if (result_user and result_admin) or (result_admin and not result_user):
        return result_admin
    elif result_user and not result_admin:
        return result_user
    else:
        return bucket


def get_autocomplete(user_id):
    default_dice = ["d20", "2d20/dl:1+4", "4d6/dl:1", "dF", "1d8+1d4"]
    try:
        secure = (str(user_id),)
        raw_dice = select_all_sql(db_user, autocomplete_get_all, secure)
    except sqlite3.OperationalError:
        return default_dice
    if raw_dice:
        dice = [d[0] for d in raw_dice]
        return dice
    else:
        return default_dice


def update_stat(discord_id, dice_number, db_type):
    if db_type == 0:
        db = db_admin
    else:
        db = db_user
    try:
        secure = (discord_id,)
        secure_update = (dice_number, discord_id)
        execute_list = [(stat_insert, secure), (stat_update, secure_update)]
        apply_sql(db, execute_list)
    except sqlite3.OperationalError:
        pass


def update_autocomplete(user_id, dice):
    try:
        secure = (user_id,)
        secure_update = (user_id, dice)
        execute_list = [(autocomplete_update, secure_update)]
        apply_sql(db_user, execute_list)
        autocomplete_number = select_sql(db_user, autocomplete_count, secure)
        if autocomplete_number >= 10:
            execute_list = [(autocomplete_delete, secure)]
            apply_sql(db_user, execute_list)
    except sqlite3.OperationalError:
        pass
