CREATE TABLE IF NOT EXISTS "capacity" (
	"discord_id"            VARCHAR(255) NOT NULL UNIQUE,
	"capacity_shortcut"     INTEGER NOT NULL,
	"capacity_custom"       INTEGER NOT NULL,
	PRIMARY KEY("discord_id")
);