# INFO FOR CMD:
cogs = {
    "Community": ["hlp", "hello", "about"],
    "Jokes": ["joke"],
    "Roll": ["roll"],
    "Context Menu": ["T2R", "RB"],
    "Server (admin only)": ["config"],
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
    "config": {
        "enabled": True,
        "name": "config",
        "usage": "",
        "aliases": "No aliases",
        "brief": "Allow to manage settings (/ only)",
        "help": "Allow to manage bot settings for this server (/)"
    },
    "T2R": {
        "enabled": True,
        "name": "T2R",
        "usage": "Apps -> Text to Roll",
        "aliases": "No aliases",
        "brief": "Find dice in chat message and roll it",
        "help": "Scanning text of message for valid dice and roll it"
    },
    "RB": {
        "enabled": True,
        "name": "RB",
        "usage": "Apps -> Report Bug",
        "aliases": "No aliases",
        "brief": "Allow to report bug",
        "help": "Get technical info from message, add provided description and send to developer"
    }
}
