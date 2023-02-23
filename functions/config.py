import configparser

# get params from config
config = configparser.ConfigParser()
# TODO: change how to get config file
config.read_file(open("config"))

# bot section
bot_token = config.get("bot", "token")
default_shards = config.getint("bot", "shards")
default_prefix = config.get("bot", "default_prefix")
dev_link = config.get("bot", "dev_link")

# topgg section
send_stat = config.getboolean("topgg", "send_stat")
topgg_token = config.get("topgg", "token")

# databases section
jokes_db = config.get("db", "jokes_db")
admin_db = config.get("db", "admin_db")

# directories
feedback_dir = config.get("dirs", "feedback_dir")
jokes_dir = config.get("dirs", "jokes_dir")

# logs
log_file = config.get("logs", "log_file")
