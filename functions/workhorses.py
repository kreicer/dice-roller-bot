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
from models.metrics import dice_edge_counter, edge_valid, postfix_counter


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


class DiceBucket:
    def __init__(self, components: dict):
        self.throws = components["throws"]
        self.edge = components["edge"]
        self.type = components["type"]
        self.dice = []
        self.log = ["all"]
        if self.type == 3:
            self.log.append("F")
        elif 4 <= self.type <= 5:
            self.log.append("Darkness")
        if "postfix" in components.keys():
            self.postfix = components["postfix"]
            self.postfixlabel = postfixes[self.postfix]["name"].replace(" ", "_").lower()
            self.value = components["value"]

        else:
            self.postfix = False
            self.postfixlabel = False
            self.value = False

    def roll(self):
        # handle logs
        for edge in self.log:
            dice_edge_counter.labels(edge).inc(self.throws)
        if self.postfixlabel:
            postfix_counter.labels(self.postfixlabel)
            postfix_counter.labels(self.postfixlabel).inc()

        # setup arguments for the Dice class and handle relevant postfixes
        end = self.throws
        dice_args = [self.type, self.edge, self.postfix == "rr"]
        if self.value:
            dice_args.append(self.value)
        if self.postfix == "x":
            end *= self.value

        # roll the dice
        i = 0
        while i < end:
            i += 1
            dice = Dice(*dice_args)
            dice.roll()
            self.dice.append(dice)

            # handle the postfixes related to each dice object.
            if (self.postfix in ["exp", "cod"] and dice.result >= self.value) or \
               (self.postfix == "wod" and dice.result == 10):
                end += 1
            elif self.postfix == "pen":
                armor = 0
                while dice.result >= self.value:
                    armor += 1
                    dice = Dice(self.type, self.edge)
                    dice.armor = armor
                    dice.roll()
                    self.dice.append(dice)

        # handle postfixes related to the finished list of dice
        if (self.postfix not in ["dl", "kl", "kh", "dh"]) or (len(self.dice) <= self.value):
            return
        else:
            self.dice.sort()
            match self.postfix:
                case "dl":
                    self.dice = self.dice[self.value:]
                case  "dh":
                    self.dice = self.dice[:-self.value]
                case  "kh":
                    self.dice = self.dice[-self.value:]
                case  "kl":
                    self.dice = self.dice[:self.value]
                case _:  # default case
                    return

    def text(self):
        # return the printed version of the dice list
        results = []
        for i in self.dice:
            results.append(str(i))
        return results

    def sum(self):
        return sum(self.dice)


class Dice:
    # types:
    # 1-2 = Standard (d4, d6, d8 etc)
    # 3 = Fate
    # 4 = Chronicles of Darkness
    # 5 = World of Darkness
    def __init__(self, dice_type: int, edge, rr=False, value: int = 0):
        self.type = dice_type
        self.edge = edge
        self.result = 0
        self.min = 1
        self.math_value = 0
        self.armor = 0
        if value > 0:
            self.value = value
            if rr:
                self.min = self.value+1

    def roll(self):
        # handle Fate rolls
        if self.type == 3:
            self.edge = 3
            self.result = random.randint(1, 3)
            self.result -= min(self.armor, self.result)  # not typically seen in this game system
            self.math_value = self.result - 2

        else:
            # handle standard dice rolls
            self.result = random.randint(self.min, self.edge)
            self.result -= min(self.armor, self.result)  # Make sure we don't subtract into negative values.
            match self.type:
                case 4:
                    self.math_value = int(self.result >= 8)
                case 5:
                    self.math_value = int(self.result >= self.value)
                    self.math_value -= int(self.result == 1)
                case _:
                    self.math_value = self.result

    # Give the dice built in operations so that values can be determined with builtin functions
    # instead of needing special functions for the class.
    def __repr__(self):
        # allows for print(dice) command to natively show the text version of the dice.
        result = self.result
        important = []
        match self.type:
            case 3:
                result = "-.+"[result - 1]
                important.extend(["-", "+"])
            case 4:
                important.extend([8, 9, 10])
            case 5:
                important.append(1)
                for i in range(self.value, 11):
                    important.append(i)
            case _:
                if self.edge == 20:
                    important.extend([1, 20])
        if result in important:
            return f'[{result}]'  # make the important results bold
        return f'{result}'

    def __radd__(self, other):
        return self.math_value + other

    def __add__(self, other):
        return self.math_value + other

    def __lt__(self, other):
        return self.result < other

    def __gt__(self, other):
        return self.result > other

    def __le__(self, other):
        return self.result <= other

    def __ge__(self, other):
        return self.result >= other

    def __eq__(self, other):
        return self.result == other


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
