# INFO FOR CMD:
cogs = {
    "Community": ["hlp", "hello", "about"],
    "Jokes": ["joke"],
    "Roll": ["roll", "postfix"],
    "Server": ["prefix"]
}


cmds = {
    "about": {
        "enabled": True,
        "name": "about",
        "usage": "",
        "aliases": ["bot", "version", "stat"],
        "brief": "Show info about the bot",
        "help": "Show info about the bot and provide links on Github, Top.gg etc"
    },
    "hello": {
        "enabled": True,
        "name": "hello",
        "usage": "",
        "aliases": ["hi"],
        "brief": "Show quick start message",
        "help": "Show extended quick start message about base dice model and provide roll examples"
    },
    "hlp": {
        "enabled": True,
        "name": "help",
        "usage": "",
        "aliases": ["support", "feedback"],
        "brief": "Show help message",
        "help": "Show commands list and info about each command"
    },
    "joke": {
        "enabled": True,
        "name": "joke",
        "usage": "",
        "aliases": ["j"],
        "brief": "All about roleplay jokes",
        "help": "Allow hear or tell jokes, also contain link to jokes channel on Community Server"
    },
    "roll": {
        "enabled": True,
        "name": "roll",
        "usage": "<throws>d<edge>/<postfix>:<value>",
        "aliases": ["r", "mod", "m"],
        "brief": "Roll the dice",
        "help": f"Roll different type of dice in one roll.\nDice examples:\n"
                f"  - single dice: 4d20\n"
                f"  - single dice with modifiers: 3d8+d4-1\n"
                f"  - multiple dice with (or without) modifiers: 2d4-1 d8 3d20-3d2\n"
                f"  - single dice with Postfix: 3d20/dl:1\n"
                f"  - single dice with Postfix and modifiers: 2d8/dh+2\n"
                f"  - multiple dice with Postfix and modifiers: 3d6/exp+2 2d20/dl-1\n"
                f"  - fate/fudge dice: 4d6/fate, d4+2d6/fate, 10d6/fate-5\n"
                f"  - Chronicles of Darkness & World of Darkness dice: These 6d10/cod and 6d10/wod.\n"
                f"   - Both of these support modifiers (6d10/cod:9, 6d10/wod:7) where the modifier is your \n"
                f"   - 8-again/9-again for CoD and your difficulty rating for WoD. WoD difficulty defaults to 6."
    },
    "postfix": {
        "enabled": True,
        "name": "postfix",
        "usage": "",
        "aliases": ["px"],
        "brief": "List Postfixes",
        "help": "Post full list of Postfixes with usage and examples"
    },
    "prefix": {
        "enabled": True,
        "name": "prefix",
        "usage": "",
        "aliases": ["p"],
        "brief": "Manage bot prefix (admin only)",
        "help": "Manage prefix for the bot commands (admin only)"
    },
    "shortcut": {
        "enabled": False,
        "name": "shortcut",
        "usage": "",
        "aliases": ["srt"],
        "brief": "Manage server's shortcuts (admin only)",
        "help": "Manage server's shortcuts for all users on server (admin only)"
    }
}
# =================
# prefix
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
# info for command shortcut
shortcut = {
    "name": "shortcut",
    "usage": "",
    "aliases": ["srt"],
    "brief": "Manage server's shortcuts (admin only)",
    "help": "Manage server's shortcuts for all users on server"
}
# info for command shortcut
shortcut_list = {
    "name": "list",
    "usage": "",
    "aliases": ["srt_list"],
    "brief": "List server's shortcuts",
    "help": "List all server's shortcuts"
}
# info for command shortcut
shortcut_add = {
    "name": "add",
    "usage": "word dice",
    "aliases": ["srt_add"],
    "brief": "Add new shortcut",
    "help": "Add new shortcut on the server for all users"
}
# info for command shortcut
shortcut_remove = {
    "name": "remove",
    "usage": "shortcut",
    "aliases": ["srt_rmv"],
    "brief": "Remove existing shortcut",
    "help": "Remove existing shortcut from server for all users"
}
