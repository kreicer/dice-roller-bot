import prometheus_client
from prometheus_client import Counter

prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)

# metrics for commands
commands_counter = Counter("commands_counter", "Counter for commands", ["command"])

# power words usage
pw_counter = Counter("pw_counter", "Counter for powerword usage", ["postfix"])

# guilds join and leave
guilds_counter = Counter("guilds_counter", "Counter for guilds", ["status"])

# dice edges
dice_edge_counter = Counter("dice_edge_counter", "Counter for dice", ["edge"])
