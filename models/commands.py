from lang.list import available_languages as lang_list

# info for command about
about = {
    "name": "about",
    "usage": "",
    "aliases": ["bot", "version"],
    "brief": "Show info about the bot",
    "help": "Show developer, bot version, Privacy Policy, link on Github, link on top.gg etc"
}
# info for command stat
stat = {
    "name": "stat",
    "usage": "",
    "aliases": ["st"],
    "brief": "Show bot statistics",
    "help": "Show number of shards and servers"
}
# info for command hello
hello = {
    "name": "hello",
    "usage": "",
    "aliases": ["hi"],
    "brief": "Show extended quick start message",
    "help": "Dice Roller tell you about base dice model and provide roll examples"
}
# info for command joke
joke = {
    "name": "joke",
    "usage": "",
    "aliases": ["j"],
    "brief": "Command to get or tell jokes",
    "help": "Command to get or tell DnD or another roleplay jokes"
}
# info for subcommand tell command joke
joke_tell = {
    "name": "tell",
    "usage": "LANG",
    "aliases": ["tell"],
    "brief": "Tell a roleplay joke",
    "help": f"Submit a joke for bot.\n"
            f"Select LANG for joke from list:\n{lang_list}\n"
            f"Add joke text in quotation marks."
}
# info for subcommand hear command joke
joke_hear = {
    "name": "hear",
    "usage": "LANG",
    "aliases": ["hear"],
    "brief": "Get a roleplay joke",
    "help": "Bot post a random roleplay joke from collection"
}
# info for command roll
roll = {
    "name": "roll",
    "usage": "dice_1 [dice_2 ... dice_n]",
    "aliases": ["r", "mod", "m"],
    "brief": "Roll the dice",
    "help": f"Roll different type of dice in one roll. Dice examples:\n \
            - single dice: 4d20\n \
            - single dice with modifiers: 3d8+d4-1\n \
            - multiple dice with (or without) modifiers: 2d4-1 d8 3d20-3d2\n \
            - single dice with Postfix: 3d20/dl:1\n \
            - single dice with Postfix and modifiers: 2d8/dh+2\n \
            - multiple dice with Postfix and modifiers: 3d6/exp+2 2d20/dl-1"
}
# info for command prefix
prefix = {
    "name": "prefix",
    "usage": "",
    "aliases": ["p"],
    "brief": "Manage bot prefix (admin only)",
    "help": "Manage prefix for the bot commands"
}
# info for subcommand set command prefix
prefix_set = {
    "name": "set",
    "usage": "",
    "aliases": ["ps"],
    "brief": "Set new prefix for the bot commands",
    "help": "Set new prefix for the bot commands, it should be 3 or less symbols."
}
# info for subcommand restore command prefix
prefix_restore = {
    "name": "restore",
    "usage": "",
    "aliases": ["pr"],
    "brief": "Restore default prefix for the bot commands",
    "help": "Restore default prefix for the bot commands (can be found in bot description)"
}
# ROOT: command for generating aliases dictionary
generate_aliases = {
    "name": "aliases",
    "usage": "",
    "aliases": ["ga"],
    "brief": "Command for manual aliases dictionary generation",
    "help": "Command for manual aliases dictionary generation.\n \
            May be helpful after adding new postfixes."
}
extension = {
    "name": "cog",
    "usage": "",
    "aliases": ["cg"],
    "brief": "Manage bot cogs (owner only)",
    "help": "Commands for manual load and unload cogs"
}
extension_list = {
    "name": "list",
    "usage": "",
    "aliases": ["cog_l"],
    "brief": "List extensions",
    "help": "Post full list of extensions (cogs)"
}
extension_load = {
    "name": "load",
    "usage": "",
    "aliases": ["cog_ld"],
    "brief": "Load extension by it's name",
    "help": "Load extension by it's name"
}
extension_unload = {
    "name": "unload",
    "usage": "",
    "aliases": ["cog_ud"],
    "brief": "Unload extension by it's name",
    "help": "Unload extension by it's name"
}
feedback = {
    "name": "feedback",
    "usage": "",
    "aliases": ["f"],
    "brief": "Send your feedback to developers team",
    "help": "Send your feedback to developers team"
}
postfix = {
    "name": "postfix",
    "usage": "",
    "aliases": ["px"],
    "brief": "List Postfixes",
    "help": "Post full list of Postfixes with usage and examples"
}

support = {
    "name": "support",
    "usage": "",
    "aliases": ["sup"],
    "brief": "Invite you to support server",
    "help": "Invite you to community support server where you can ask for help, suggest improvement or just chat"
}
