from functions.checks import check_postfix_is_right_and_available, check_action_is_right_and_available
from functions.colorizer import Colorizer
from functions.config import bot_name, bot_version, dev_name, bot_shards
from lang.EN.texts import command_shortcut_text, command_prefix_text, command_action_text, command_postfix_text
from models.actions import actions
from models.postfixes import postfixes
from models.commands import cmds


def generate_postfix_short_output():
    output = f"<green>POSTFIXES<end>\n\n"
    output += command_postfix_text + "\n\n"
    for postfix in postfixes:
        if postfixes[postfix]["enabled"]:
            output += f"  <green>{postfix: <7}<end>{postfixes[postfix]['shorty']}\n"
    output += "\n"
    output += "Postfix position in dice structure\n"
    output += f"<gray><throws>d<edge>/<green><postfix><gray>:<value><end>\n\n"
    output += f"<gray>For detailed info about each postfix use selector below"
    output = Colorizer(output).colorize()
    return output


def generate_postfix_help(postfix):
    check_postfix_is_right_and_available(postfix)
    default = postfixes[postfix]['default_value']
    if default == "":
        default = "max"
    output = f"<green>{postfixes[postfix]['name'].upper()}<end>\n\n"
    output += f"{postfixes[postfix]['description']}\n\n"
    output += f"Example: <blue>/{postfixes[postfix]['example']}<end>\n"
    output += f"Default value: <blue>{default}<end>"
    output = Colorizer(output).colorize()
    return output


def generate_action_short_output():
    output = f"<green>ACTIONS<end>\n\n"
    output += command_action_text + "\n\n"
    for action in actions:
        if actions[action]["enabled"]:
            output += f"  <green>{action: <14}<end>{actions[action]['shorty']}\n"
    output += "\n"
    output += "Action position in dice structure\n"
    output += f"<gray><dice>|<green><action><end>\n\n"
    output += f"<gray>For detailed info about each action use selector below"
    output = Colorizer(output).colorize()
    return output


def generate_action_help(action):
    check_action_is_right_and_available(action)
    output = f"<green>{action.upper()}<end>\n\n"
    output += f"{actions[action]['description']}\n\n"
    output += f"Example: <blue>/{actions[action]['example']}<end>\n"
    output = Colorizer(output).colorize()
    return output


def generate_joke_output(joke_id, joke_text):
    output = f"<green>Joke #{joke_id}<end>\n\n" \
             f"{joke_text}"
    output = Colorizer(output).colorize()
    return output


def generate_prefix_output(prefix, text):
    output = f"<green>PREFIX <yellow>(ADMIN ACTION)<end>\n" \
             f"{command_prefix_text}\n\n" \
             f"{text} - <blue>{prefix}<end>"
    output = Colorizer(output).colorize()
    return output


def generate_info_output(guilds_number):
    output = f"<green>{bot_name} v{bot_version} by {dev_name}<end>\n\n" \
             f"Shards: <blue>{bot_shards}<end>\n" \
             f"Servers: <blue>{guilds_number}<end>"
    output = Colorizer(output).colorize()
    return output


def generate_help_short_output(cogs_dict):
    output = f"<green>COMMANDS<end>\n\n"
    for key, value in cogs_dict.items():
        output += f"{key}:\n"
        for cmd in value:
            output += f"  <green>{cmds[cmd]['name']: <10}<end>{cmds[cmd]['brief']}\n"
        output += f"\n"
    output += f"<gray>For detailed info about each command use selector below<end>"
    output = Colorizer(output).colorize()
    return output


def generate_commands_help(command):
    if cmds[command]['name'] == "T2R":
        output = f"<green>TEXT TO ROLL<end>\n\n"
    elif cmds[command]['name'] == "RB":
        output = f"<green>REPORT BUG<end>\n\n"
    else:
        output = f"<green>{cmds[command]['name'].upper()}<end>\n\n"
    output += f"{cmds[command]['help']}\n\n"
    output += f"Aliases: <blue>{cmds[command]['aliases']}<end>\n"
    if cmds[command]['name'] == "T2R" or cmds[command]['name'] == "RB":
        output += f"Usage: <blue>{cmds[command]['usage']}<end>"
    else:
        output += f"Usage: <blue>/{cmds[command]['name']} {cmds[command]['usage']}<end>"
    output = Colorizer(output).colorize()
    return output


def generate_shortcut_output(shortcuts, number, limit):
    output = f"<green>SHORTCUTS {number}/{limit} <yellow>(ADMIN ACTION)<end>\n"
    output += command_shortcut_text + "\n\n"
    for shortcut, dice in shortcuts:
        output += f"  <green>{shortcut: <12}<end> <blue>{dice}<end>\n"
    output += "\n"
    output += f"<gray>Select one or more shortcuts to unlock remove button."
    output = Colorizer(output).colorize()
    return output


def generate_shortcut_empty_output():
    output = f"<green>SHORTCUTS <yellow>(ADMIN ACTION)<end>\n"
    output += command_shortcut_text + "\n\n"
    output += f"There are no shortcuts on your server yet."
    output = Colorizer(output).colorize()
    return output
