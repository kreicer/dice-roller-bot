# list of suffixes for roll modifications
actions = {
    "multiplier": {
        "description": "Multiply current roll on value but not more than limit",
        "shorty": "multiply current roll",
        "example": "roll 2d20/kh:1+5|x2 5d8|4",
        "enabled": True
    },
    "label": {
        "description": "Add text label to current roll, should contain no whitespace",
        "shorty": "add label to roll",
        "example": "roll 4d6/dl:1|my_stat",
        "enabled": True
    },
    "tag": {
        "description": "Add member tag to current roll, should contain no whitespace",
        "shorty": "add member tag to roll",
        "example": "roll 2d20/dl:1+5|@kreicer",
        "enabled": True
    }
}
