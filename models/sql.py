# SQL for "source" table admin.db
source_update = "INSERT OR REPLACE INTO source (discord_id, type) VALUES (?,?);"
source_delete = "DELETE FROM source WHERE discord_id = ?;"

# SQL for "prefix" table admin.db
prefix_get = "SELECT prefix FROM prefix WHERE discord_id = ?;"
prefix_update = "INSERT OR REPLACE INTO prefix (discord_id, prefix) VALUES (?,?);"
prefix_delete = "DELETE FROM prefix WHERE discord_id = ?;"

# SQL for "shortcut" table admin.db
shortcut_count = "SELECT COUNT(shortcut) FROM shortcut WHERE discord_id = ?;"
shortcut_get_all = "SELECT shortcut, dice FROM shortcut WHERE discord_id = ?;"
shortcut_get_dice = "SELECT dice FROM shortcut WHERE discord_id = ? AND shortcut = ?;"
shortcut_update = "INSERT OR REPLACE INTO shortcut (discord_id, shortcut, dice) VALUES (?,?,?);"
shortcut_delete_all = "DELETE FROM shortcut WHERE discord_id = ?;"
shortcut_delete_single = "DELETE FROM shortcut WHERE discord_id = ? AND shortcut = ?;"

# SQL for "jokes" table jokes.db
jokes_count = "SELECT COUNT(joke_id) FROM jokes;"
joke_get = "SELECT joke_text FROM jokes WHERE joke_id = ?;"
