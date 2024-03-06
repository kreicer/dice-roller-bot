CREATE TABLE IF NOT EXISTS "autocomplete" (
	"discord_id"            VARCHAR(255) NOT NULL,
	"dice"                  VARCHAR(255) NOT NULL,
	"timestamp"             DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'utc')),
	PRIMARY KEY("discord_id", "dice")
);