def detect_action_type(action):
    try:
        value = int(action.replace("x", ""))
        action_type = 1
    except ValueError:
        if "@" in action:
            action_type = 2
        else:
            action_type = 3
        value = action
    return action_type, value
