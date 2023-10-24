# list of suffixes for roll modifications
postfixes = {
    "exp": {
        "name": "Explode",
        "default_value": "",
        "description": "Modifying dice to become exploding dice: roll again when equal or higher than value.",
        "shorty": "modify dice to become explode dice",
        "example": "roll 2d20/exp",
        "enabled": True
    },
    "pen": {
        "name": "Penetrate",
        "default_value": "",
        "description": "Modifying dice to become penetrating dice: roll again when equal or higher than value. "
                       "But 1 will be subtracted from the result of that additional roll.",
        "shorty": "modify dice to become penetration dice",
        "example": "roll 2d20/pen",
        "enabled": True
    },
    "sts": {
        "name": "Stress",
        "default_value": 1,
        "description": "Roll additional part of dice if no maximum on first roll.",
        "shorty": "modify dice to become stress dice",
        "example": "roll 4d6/sts",
        "enabled": False
    },
    "dl": {
        "name": "Drop Lowest",
        "default_value": 1,
        "description": "Drop specified number of dice with lowest number",
        "shorty": "drop dice with lowest result",
        "example": "roll 10d20/dl:3",
        "enabled": True
    },
    "dh": {
        "name": "Drop Highest",
        "default_value": 1,
        "description": "Drop specified number of dice with highest number",
        "shorty": "drop dice with highest result",
        "example": "roll 5d10/dh:2",
        "enabled": True
    },
    "kl": {
        "name": "Keep Lowest",
        "default_value": 1,
        "description": "Keep specified number of dice with lowest number",
        "shorty": "keep dice with lowest result",
        "example": "roll 4d100/kl:1",
        "enabled": True
    },
    "kh": {
        "name": "Keep Highest",
        "default_value": 1,
        "description": "Keep specified number of dice with highest number",
        "shorty": "keep dice with highest result",
        "example": "roll 3d4/kh:1",
        "enabled": True
    },
    "rr": {
        "name": "ReRoll",
        "default_value": 1,
        "description": "Reroll dice with result on value or lower",
        "shorty": "reroll dice",
        "example": "roll 2d20/rr:2",
        "enabled": True
    },
    "min": {
        "name": "Minimum",
        "default_value": 1,
        "description": "Set minimum value for dice roll result",
        "shorty": "minimum dice roll result",
        "example": "roll 6d20/min:10",
        "enabled": True
    },
    "c": {
        "name": "Counter",
        "default_value": "",
        "description": "Count roll results with value or higher",
        "shorty": "count dice roll results",
        "example": "roll 10d8/c:7",
        "enabled": True
    },
    "suc": {
        "name": "Success",
        "default_value": "",
        "description": "Count roll results with value of higher as +1 (success) and 1 as -1 (fail)",
        "shorty": "count success and fail",
        "example": "roll 7d12/suc:10",
        "enabled": True
    },
    "div": {
        "name": "Divisor",
        "default_value": 1,
        "description": "Divides the roll result by the value and rounds up",
        "shorty": "divides with round up",
        "example": "roll 4d8/div:2",
        "enabled": True
    },
    "mul": {
        "name": "Multiplier",
        "default_value": 1,
        "description": "Multiply the roll result by the value",
        "shorty": "multiply result",
        "example": "roll 5d2/mul:6",
        "enabled": True
    }
}
