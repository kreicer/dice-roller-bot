from lang.EN.errors import wrong_dice_error, wrong_sign_error, zero_throws_error, throws_limit_error, zero_mod_error, \
    mod_limit_error, zero_edge_error, edge_limit_error, empty_postfix_error, bad_postfix_error, value_vs_throws_error, \
    value_vs_edge_error, edge_vs_two_error, infinity_loop_error, value_for_multiply_error, postfix_right_error, \
    shortcut_name_error, shortcut_limit_error, action_right_error
from lang.list import available_languages as lang_list
from models.actions import actions
from models.postfixes import postfixes as postfix_dict, postfixes
from discord.ext import commands
from pathlib import Path
from models.limits import edge_limit as e_limit, roll_limit as r_limit, modifier_limit as m_limit, group_limit


# check limits
def check_limit(number, limit, for_error):
    if number > limit:
        raise commands.ArgumentParsingError(None, for_error)


def check_lang(language, for_error):
    if language not in lang_list:
        raise commands.BadArgument(None, for_error)


def check_match(match):
    if match is None:
        error_text = wrong_dice_error
        raise commands.BadArgument(None, error_text)


def check_file_exist(filename):
    exist_file = Path(filename)
    if exist_file.is_file():
        raise commands.BadArgument


def check_dice_dict(dice_dict):
    dice_dict["mod"] = check_mod(dice_dict["mod"])
    if dice_dict["delimiter"] == "d":
        dice_dict["throws"] = check_throws(dice_dict["throws"])
        dice_dict["edge"] = check_edge(dice_dict["edge"])
        if isinstance(dice_dict["edge"], int):
            dice_dict["type"] = 1
        else:
            dice_dict["type"] = 3
    else:
        dice_dict["throws"] = check_modifier(dice_dict["throws"])
        dice_dict["type"] = 0
    if dice_dict["separator"] == "/":
        dice_dict["postfix"] = check_postfix(dice_dict["postfix"], postfixes.keys())
        default_value = postfix_dict[dice_dict["postfix"]]["default_value"]
        dice_dict["value"] = check_value(dice_dict["value"], default_value)
        dice_dict["type"] = 2
    dice_dict.pop("delimiter")
    dice_dict.pop("separator")
    return dice_dict


def check_mod(mod):
    cleared_mod = "".join(set(mod))
    if cleared_mod == "":
        cleared_mod = "+"
    elif cleared_mod not in ["+", "-"]:
        error_text = wrong_sign_error
        raise commands.BadArgument(None, error_text)
    return cleared_mod


def check_throws(throws):
    if throws == "":
        throws = 1
    elif throws == "0":
        error_text = zero_throws_error
        raise commands.BadArgument(None, error_text)
    else:
        throws = int(throws)
        error_text = throws_limit_error.format(throws, r_limit)
        check_limit(throws, r_limit, error_text)
    return throws


def check_modifier(throws):
    if throws == "0":
        error_text = zero_mod_error
        raise commands.BadArgument(None, error_text)
    else:
        throws = int(throws)
        error_text = mod_limit_error.format(throws, m_limit)
        check_limit(throws, m_limit, error_text)
    return throws


def check_edge(edge):
    if edge == "0" or edge == "":
        error_text = zero_edge_error
        raise commands.BadArgument(None, error_text)
    elif edge.upper() == "F":
        edge = "F"
    else:
        edge = int(edge)
        error_text = edge_limit_error.format(edge, e_limit)
        check_limit(edge, e_limit, error_text)
    return edge


def check_postfix(postfix, postfixes_keys):
    if postfix == "":
        error_text = empty_postfix_error
        raise commands.BadArgument(None, error_text)
    elif postfix not in postfixes_keys:
        error_text = bad_postfix_error
        raise commands.BadArgument(None, error_text)
    return postfix


def check_value(value, defaults):
    if value == "" or value == "0":
        value = defaults
    else:
        value = int(value)
    return value


def check_value_vs_throws(throws, value):
    if value >= throws:
        error_text = value_vs_throws_error
        raise commands.BadArgument(None, error_text)


def check_value_vs_edge(edge, value):
    if value > edge:
        error_text = value_vs_edge_error
        raise commands.BadArgument(None, error_text)


def check_edge_vs_two(edge):
    if edge < 2:
        error_text = edge_vs_two_error
        raise commands.BadArgument(None, error_text)


def check_value_for_infinity_loop(value):
    if value == 1:
        error_text = infinity_loop_error
        raise commands.BadArgument(None, error_text)


def check_multiply(args_len):
    if args_len > group_limit:
        error_text = value_for_multiply_error.format(group_limit)
        raise commands.BadArgument(None, error_text)


def check_postfix_is_right_and_available(postfix):
    if postfix not in postfix_dict.keys():
        error_text = postfix_right_error
        raise commands.BadArgument(None, error_text)


def check_action_is_right_and_available(action):
    if action not in actions.keys():
        error_text = action_right_error
        raise commands.BadArgument(None, error_text)


def check_shortcut_name(shortcut_name):
    if not shortcut_name.isalnum():
        error_text = shortcut_name_error
        raise commands.BadArgument(None, error_text)


def check_shortcut_limit(shortcut_amount, shortcut_limit, shortcut_exist):
    if int(shortcut_amount) >= shortcut_limit and not shortcut_exist:
        error_text = shortcut_limit_error
        raise commands.TooManyArguments(None, error_text)
