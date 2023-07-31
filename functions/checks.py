from lang.list import available_languages as lang_list
from models.postfixes import postfixes as postfix_dict, aliases as aliases_dict
from discord.ext import commands
from pathlib import Path
from models.limits import edge_limit as e_limit, roll_limit as r_limit, modifier_limit as m_limit


# check limits
def check_limit(number, limit, for_error):
    if number > limit:
        raise commands.ArgumentParsingError(None, for_error)


def check_lang(language, for_error):
    if language not in lang_list:
        raise commands.BadArgument(None, for_error)


def check_match(match):
    if match is None:
        error_text = "Wrong dice or modifier.\n" \
                     "Dice pattern is *[throws]*d*[edge]*/*[postfix]*:*[value]*.\n" \
                     "Fate/Fudge dice pattern is *[throws]*d*F*.\n"\
                     "Modifier should start from + or - and can be another dice or number."
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
        dice_dict["postfix"] = check_postfix(dice_dict["postfix"], aliases_dict)
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
        error_text = "Dice modifiers can be additive (+) or subtractive (-) only."
        raise commands.BadArgument(None, error_text)
    return cleared_mod


def check_throws(throws):
    if throws == "":
        throws = 1
    elif throws == "0":
        error_text = "Number of dice throws can not be zero."
        raise commands.BadArgument(None, error_text)
    else:
        throws = int(throws)
        error_text = f"Number of throws ({throws}) is greater than the current limit of {r_limit}"
        check_limit(throws, r_limit, error_text)
    return throws


def check_modifier(throws):
    if throws == "0":
        error_text = "Modifier can not be zero."
        raise commands.BadArgument(None, error_text)
    else:
        throws = int(throws)
        error_text = f"Modifier ({throws}) is greater than the current limit of {m_limit}"
        check_limit(throws, m_limit, error_text)
    return throws


def check_edge(edge):
    if edge == "0" or edge == "":
        error_text = "Value of dice edge can not be zero or empty."
        raise commands.BadArgument(None, error_text)
    elif edge.upper() == "F":
        edge = "F"
    else:
        edge = int(edge)
        error_text = f"Dice edge value ({edge}) is greater than the current limit of {e_limit}"
        check_limit(edge, e_limit, error_text)
    return edge


def check_postfix(postfix, aliases):
    if postfix == "":
        error_text = "Alias to \"Postfix\" can not be empty."
        raise commands.BadArgument(None, error_text)
    elif postfix not in aliases.keys():
        error_text = "Can not find this alias to existing \"Postfix\".\n" \
                     "You can list all available \"Postfixes\" with: ```/postfix```"
        raise commands.BadArgument(None, error_text)
    else:
        postfix = aliases[postfix]
    return postfix


def check_value(value, defaults):
    if value == "" or value == "0":
        value = defaults
    else:
        value = int(value)
    return value


def check_value_vs_throws(throws, value):
    if value >= throws:
        error_text = "Value can not be higher or equal to number of throws in this Postfix."
        raise commands.BadArgument(None, error_text)


def check_value_vs_edge(edge, value):
    if value > edge:
        error_text = "Value can not be higher than dice edge in this Postfix."
        raise commands.BadArgument(None, error_text)


def check_edge_vs_two(edge):
    if edge < 2:
        error_text = "Can not use this Postfix with dice edge equal to 1."
        raise commands.BadArgument(None, error_text)


def check_value_for_explode(value):
    if value == 1:
        error_text = "Exploding dice can not be rolled with value equal to 1 - protection from infinity loop"
        raise commands.BadArgument(None, error_text)


def check_value_for_penetrate(value):
    if value == 1:
        error_text = "Penetrating dice can not be rolled with value equal to 1 - protection from infinity loop"
        raise commands.BadArgument(None, error_text)


def check_value_for_multiply(throws, value):
    if value > r_limit:
        error_text = f"Multiplier value cannot be higher than current rolls limit {r_limit}"
        raise commands.BadArgument(None, error_text)
    elif throws * value > r_limit:
        error_text = f"Multiplied throws number cannot be higher than current roll limit {r_limit}"
        raise commands.BadArgument(None, error_text)


def check_postfix_is_right_and_available(postfix):
    if postfix not in postfix_dict.keys():
        error_text = "Can not find this short name to existing \"Postfix\".\n" \
                     "You can list all available \"Postfixes\" with: ```/postfix```"
        raise commands.BadArgument(None, error_text)
