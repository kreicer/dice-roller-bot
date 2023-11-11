import prometheus_client
from prometheus_client import Counter
from functions.config import metrics_python_ext

if metrics_python_ext is False:
    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)

# metrics for buckets
buckets_counter = Counter("buckets_counter", "Counter for buckets", ["number_of_buckets"])

# metrics for commands
commands_counter = Counter("commands_counter", "Counter for commands", ["command"])

# postfix usage
postfix_counter = Counter("postfix_counter", "Counter for postfix usage", ["postfix"])

# action usage
action_counter = Counter("action_counter", "Counter for action usage", ["action"])

# guilds join and leave
guilds_counter = Counter("guilds_counter", "Counter for guilds", ["status"])

# dice edges
edge_valid = [2, 4, 6, 8, 10, 12, 20, 100]
dice_edge_counter = Counter("dice_edge_counter", "Counter for dice", ["edge"])

# errors
errors_counter = Counter("errors_counter", "Counter for errors of all type", ["command", "error"])

# ui
ui_counter = Counter("ui_counter", "Counter for UI", ["ui_type", "command", "label"])
ui_errors_counter = Counter("ui_errors_counter", "Counter for errors in UI", ["ui_type", "command", "error"])
