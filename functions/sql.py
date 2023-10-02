import sqlite3

from functions.config import log_file


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
        raise sqlite3.OperationalError
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
        # raise sqlite3.OperationalError
        print("zalupa")
    return result


def select_all_sql(database, sql, arguments):
    result = ""
    try:
        db = sqlite3.connect(database)
        cur = db.cursor()
        cur.execute(sql, arguments)
        query_result = cur.fetchall()
        db.close()
        result = query_result
    except sqlite3.OperationalError:
        raise sqlite3.OperationalError
    return result
