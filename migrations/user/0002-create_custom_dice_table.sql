CREATE TABLE IF NOT EXISTS "custom_dice" (
	"discord_id"            VARCHAR(255) NOT NULL,
	"dice"                  VARCHAR(255) NOT NULL,
	"values"                VARCHAR(255) NOT NULL,
	PRIMARY KEY("discord_id", "dice"),
	FOREIGN KEY("discord_id") REFERENCES source("discord_id")
);