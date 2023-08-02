import prometheus_client
from prometheus_client import Counter
from functions.config import metrics_python_ext

if metrics_python_ext is False:
    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)

# metrics for commands
commands_counter = Counter("commands_counter", "Counter for commands", ["command"])

# postfix usage
postfix_counter = Counter("postfix_counter", "Counter for postfix usage", ["postfix"])

# guilds join and leave
guilds_counter = Counter("guilds_counter", "Counter for guilds", ["status"])

# dice edges
edge_valid = [2, 4, 6, 8, 10, 12, 20, 100]
dice_edge_counter = Counter("dice_edge_counter", "Counter for dice", ["edge"])

# errors
errors_counter = Counter("errors_counter", "Counter for errors of all type", ["command", "error"])

# ui buttons
ui_button_counter = Counter("ui_button_click_counter", "Counter for buttons", ["cmd", "button"])

# ui modals
ui_modals_counter = Counter("ui_modals_submit_counter", "Counter for modals", ["cmd", "modal"])

# ui errors
ui_errors_counter = Counter("ui_errors_counter", "Counter for errors in ui", ["cmd", "ui", "error"])
