CREATE TABLE IF NOT EXISTS "source" (
	"discord_id"            VARCHAR(255) NOT NULL UNIQUE,
	"last_interation"       DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'utc')),
	PRIMARY KEY("discord_id")
);