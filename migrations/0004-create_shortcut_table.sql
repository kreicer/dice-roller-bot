CREATE TABLE IF NOT EXISTS "shortcut" (
	"discord_id"	VARCHAR(255) NOT NULL,
	"shortcut"	VARCHAR(255) NOT NULL,
	"dice"	VARCHAR(255) NOT NULL,
	PRIMARY KEY("discord_id", "shortcut"),
	FOREIGN KEY("discord_id") REFERENCES source("discord_id")
)