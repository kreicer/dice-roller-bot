from datetime import datetime
from functions.config import log_file


def logger(filename, log_level, text) -> None:
    with open(filename, 'a') as file:
        print(datetime.now(), log_level, text, file=file)
    file.close()


def log_info(text) -> None:
    log_txt = text
    logger(log_file, "INFO", log_txt)


def log_error(error) -> None:
    log_txt = type(error) + "\n" + error + "\n" + error.__traceback__
    logger(log_file, "ERROR", log_txt)
