CREATE TABLE IF NOT EXISTS "shortcut" (
	"guild_id"	INTEGER NOT NULL,
	"shortcut"	VARCHAR(255) NOT NULL,
	"dice"	VARCHAR(255) NOT NULL,
	PRIMARY KEY("guild_id"),
	FOREIGN KEY("guild_id") REFERENCES source("id")
)