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
bot_token = config.get("bot", "token")
bot_shards = config.getint("bot", "shards")
bot_prefix = config.get("bot", "prefix")

# developer section
dev_name = config.get("developer", "name")
dev_link = config.get("developer", "link")
dev_github = config.get("developer", "github_link")

# community section
community_policy = config.get("community", "policy")
community_support = config.get("community", "support")

# topgg section
topgg_enable = config.getboolean("topgg", "enable")
topgg_timer = config.getint("topgg", "timer")
topgg_link = config.get("topgg", "link")
topgg_token = config.get("topgg", "token")

# metrics section
metrics_enable = config.getboolean("metrics", "enable")
metrics_port = config.getint("metrics", "port")
metrics_python_ext = config.getboolean("metrics", "python_ext")

# databases section
db_jokes = config.get("db", "jokes")
db_admin = config.get("db", "admin")
db_user = config.get("db", "user")

# directories
dir_feedback = config.get("dir", "feedback")
dir_jokes = config.get("dir", "jokes")
dir_bugs = config.get("dir", "bugs")

# logs
log_file = config.get("log", "file")
