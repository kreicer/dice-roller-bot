# SQL for "jokes" table jokes.db
jokes_count = "SELECT COUNT(joke_id) FROM jokes;"
joke_get = "SELECT joke_text FROM jokes WHERE joke_id = ?;"
