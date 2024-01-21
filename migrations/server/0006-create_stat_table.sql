CREATE TABLE IF NOT EXISTS "stat" (
	"discord_id"            VARCHAR(255) NOT NULL UNIQUE,
	"stat_dice"             INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("discord_id")
);