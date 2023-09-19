# SQL for "source" table admin.db
source_update = "INSERT OR REPLACE INTO source (discord_id, type) VALUES (?,?);"
source_delete = "DELETE FROM source WHERE discord_id = ?;"

# SQL for "prefix" table admin.db
prefix_get = "SELECT prefix FROM prefix WHERE discord_id = ?;"
prefix_update = "INSERT OR REPLACE INTO prefix (discord_id, prefix) VALUES (?,?);"
prefix_delete = "DELETE FROM prefix WHERE discord_id = ?;"

# SQL for "shortcut" table admin.db
shortcut_delete = "DELETE FROM shortcut WHERE discord_id = ?;"

# SQL for "jokes" table jokes.db
jokes_count = "SELECT COUNT(joke_id) FROM jokes;"
joke_get = "SELECT joke_text FROM jokes WHERE joke_id = ?;"
