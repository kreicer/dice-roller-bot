# SQL for "shortcut" table user.db
shortcut_count = "SELECT COUNT(shortcut) FROM shortcut WHERE discord_id = ?;"
shortcut_get_all = "SELECT shortcut, dice FROM shortcut WHERE discord_id = ?;"
shortcut_get_dice = "SELECT dice FROM shortcut WHERE discord_id = ? AND shortcut = ?;"
shortcut_update = "INSERT OR REPLACE INTO shortcut (discord_id, shortcut, dice) VALUES (?,?,?);"
shortcut_delete_all = "DELETE FROM shortcut WHERE discord_id = ?;"
shortcut_delete_single = "DELETE FROM shortcut WHERE discord_id = ? AND shortcut = ?;"

# SQL for "stat" table user.db
stat_get_dice = "SELECT stat_dice FROM stat WHERE discord_id = ?;"
stat_insert = "INSERT OR IGNORE INTO stat (discord_id) VALUES (?);"
stat_update = "UPDATE stat SET stat_dice = stat_dice + ? WHERE discord_id = ?;"
stat_delete = "DELETE FROM stat WHERE discord_id = ?;"

# SQL for "custom_dice" table user.db
custom_dice_count = "SELECT COUNT(dice) FROM custom_dice WHERE discord_id = ?;"
custom_dice_delete_all = "DELETE FROM custom_dice WHERE discord_id = ?;"
