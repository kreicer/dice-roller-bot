def detect_action_type(action):
    try:
        int(action.replace("x", ""))
        multiplier = True
    except ValueError:
        multiplier = False
    if multiplier:
        action_type = 1
        value = int(action.replace("x", ""))
    # elif action.startswith("@") or action.startswith("#"):
    #    action_type = 2
    #    value = action.replace("@", "")
    else:
        action_type = 3
        value = action
    return action_type, value
