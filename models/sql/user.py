# SQL for "autocomplete" table: user.db
autocomplete_get_all = "SELECT dice FROM autocomplete WHERE discord_id = ?;"
autocomplete_count = "SELECT COUNT(dice) FROM autocomplete WHERE discord_id = ?;"
autocomplete_delete = ("DELETE FROM autocomplete WHERE dice in ("
                       "SELECT dice FROM autocomplete WHERE discord_id = ? ORDER BY timestamp LIMIT 1);")
autocomplete_update = "INSERT OR REPLACE INTO autocomplete (discord_id, dice) VALUES (?,?);"
