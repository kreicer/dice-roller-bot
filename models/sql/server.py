# SQL for "source" table server.db
source_update = "INSERT OR REPLACE INTO source (discord_id) VALUES (?);"
source_delete = "DELETE FROM source WHERE discord_id = ?;"

# SQL for "prefix" table server.db
prefix_get = "SELECT prefix FROM prefix WHERE discord_id = ?;"
prefix_update = "INSERT OR REPLACE INTO prefix (discord_id, prefix) VALUES (?,?);"
prefix_delete = "DELETE FROM prefix WHERE discord_id = ?;"
