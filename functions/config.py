import configparser

# get params from config
config = configparser.ConfigParser()
# TODO: change how to get config file
config_file = "config"
try:
    config.read_file(open(config_file))
except FileNotFoundError:
    log_txt = f"Failed to open config file - {config_file}"
    print("FATAL", log_txt)

# bot section
bot_name = config.get("bot", "name")
bot_version = config.get("bot", "version")
bot_dev = config.get("bot", "developer")
bot_token = config.get("bot", "token")
default_shards = config.getint("bot", "shards")
default_prefix = config.get("bot", "default_prefix")
dev_link = config.get("bot", "dev_link")

# topgg section
send_stat = config.getboolean("topgg", "send_stat")
topgg_token = config.get("topgg", "token")

# metrics section
metrics_enable = config.getboolean("metrics", "enable")
metrics_port = config.getint("metrics", "port")
metrics_python_ext = config.getboolean("metrics", "python_ext")

# databases section
jokes_db = config.get("db", "jokes_db")
admin_db = config.get("db", "admin_db")

# directories
feedback_dir = config.get("dirs", "feedback_dir")
jokes_dir = config.get("dirs", "jokes_dir")

# logs
log_file = config.get("logs", "log_file")

# link section
github = config.get("links", "github_link")
topgg = config.get("links", "topgg_link")
policy = config.get("links", "privacy_policy")
support = config.get("links", "support")
