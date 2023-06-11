from prometheus_client import Counter

# metrics for commands
commands_used_roll = Counter("commands_used_roll", "Counter for roll command")
commands_used_powerwords = Counter("commands_used_powerwords", "Counter for powerword command")
commands_used_about = Counter("commands_used_about", "Counter for about command")
commands_used_stat = Counter("commands_used_stat", "Counter for stat command")
commands_used_joke_hear = Counter("commands_used_joke_hear", "Counter for joke hear command")
commands_used_joke_tell = Counter("commands_used_joke_tell", "Counter for joke tell command")
commands_used_hello = Counter("commands_used_hello", "Counter for hello command")
commands_used_feedback = Counter("commands_used_feedback", "Counter for feedback command")
commands_used_prefix_set = Counter("commands_used_prefix_set", "Counter for prefix set command")
commands_used_prefix_restore = Counter("commands_used_prefix_restore", "Counter for prefix restore command")

# power words usage
pw_used_explode = Counter("pw_used_explode", "Counter for explode powerword usage")
pw_used_penetrate = Counter("pw_used_penetrate", "Counter for penetrate powerword usage")
pw_used_drop_lowest = Counter("pw_used_drop_lowest", "Counter for drop lowest powerword usage")
pw_used_drop_highest = Counter("pw_used_drop_highest", "Counter for drop highest powerword usage")
pw_used_reroll = Counter("pw_used_reroll", "Counter for reroll powerword usage")
