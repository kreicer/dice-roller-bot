# module and files import section
import sqlite3

conn = sqlite3.connect('jokes.db')

sql = "SELECT joke_text FROM jokes WHERE joke_id=1;"
cursor = conn.cursor()
result = cursor.execute(sql)
print(cursor.fetchone()[0])
