# INFO FOR CMD:
cogs = {
    "Community": ["hlp", "hello", "about"],
    "Jokes": ["joke"],
    "Roll": ["roll", "postfix", "action"],
    "Server": ["prefix", "shortcut"],
    "Context Menu": ["T2R"]
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
        "brief": "Show welcome message with basic info",
        "help": "Show welcome message with info about base dice model and contain roll examples"
    },
    "hlp": {
        "enabled": True,
        "name": "help",
        "usage": "",
        "aliases": ["support", "feedback"],
        "brief": "Show help message, provide other support functions",
        "help": "Show commands list and info about each command, allow send feedback and can invite to support server"
    },
    "joke": {
        "enabled": True,
        "name": "joke",
        "usage": "",
        "aliases": ["j"],
        "brief": "All about roleplay jokes",
        "help": "Allow read or tell jokes, also contain link to jokes channel on Community Server"
    },
    "roll": {
        "enabled": True,
        "name": "roll",
        "usage": "<throws>d<edge>/<postfix>:<value>",
        "aliases": ["r", "mod", "m"],
        "brief": "Roll the dice",
        "help": f"Roll different types of dice.\nDice examples:\n"
                f"  - single dice: 4d20\n"
                f"  - single dice with modifiers: 3d8+d4-1\n"
                f"  - multiple dice with (or without) modifiers: 2d4-1 d8 3d20-3d2\n"
                f"  - single dice with Postfix: 3d20/dl:1\n"
                f"  - single dice with Postfix and modifiers: 2d8/dh+2\n"
                f"  - multiple dice with Postfix and modifiers: 3d6/exp+2 2d20/dl-1\n"
                f"  - fate/fudge dice: 4dF d4+2dF 10df-5 (no postfixes)"
    },
    "postfix": {
        "enabled": True,
        "name": "postfix",
        "usage": "",
        "aliases": ["px"],
        "brief": "List all available postfixes",
        "help": "Post full list of postfixes with examples"
    },
    "action": {
        "enabled": True,
        "name": "action",
        "usage": "",
        "aliases": ["act"],
        "brief": "List all available actions",
        "help": "Post full list of actions with examples"
    },
    "prefix": {
        "enabled": True,
        "name": "prefix",
        "usage": "",
        "aliases": ["p"],
        "brief": "Manage bot prefix (server admin only)",
        "help": "Manage prefix for the bot commands (server admin only)"
    },
    "shortcut": {
        "enabled": True,
        "name": "shortcut",
        "usage": "",
        "aliases": ["srt"],
        "brief": "Manage server's shortcuts (server admin only)",
        "help": "Manage server's shortcuts for all users on server (server admin only)"
    },
    "T2R": {
        "enabled": True,
        "name": "T2R",
        "usage": "Apps -> Text to Roll",
        "aliases": "No aliases",
        "brief": "Find dice in chat message and roll it",
        "help": "Scanning text of message for valid dice and roll it"
    }
}
# =================
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
