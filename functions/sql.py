import sqlite3

from functions.config import log_file
from functions.workhorses import logger


# SQL operations functions
def apply_sql(database, sql_list):
    result = False
    try:
        db = sqlite3.connect(database)
        cur = db.cursor()
        for sql, arguments in sql_list:
            cur.execute(sql, arguments)
        db.commit()
        db.close()
        result = True
    except sqlite3.OperationalError:
        log_txt = f"Failed to load database file - {database}"
        logger(log_file, "ERROR", log_txt)
    return result


def select_sql(database, sql, arguments):
    result = ""
    try:
        db = sqlite3.connect(database)
        cur = db.cursor()
        cur.execute(sql, arguments)
        query_result = cur.fetchone()
        if query_result is not None:
            result = query_result[0]
        db.close()
    except sqlite3.OperationalError:
        log_txt = f"Failed to load database file - {database}"
        logger(log_file, "ERROR", log_txt)
    return result
