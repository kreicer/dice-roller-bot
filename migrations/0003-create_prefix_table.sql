CREATE TABLE IF NOT EXISTS "prefixes" (
	"guild_id"	INTEGER NOT NULL UNIQUE,
	"prefix"	VARCHAR(255) NOT NULL,
	PRIMARY KEY("guild_id"),
	FOREIGN KEY("guild_id") REFERENCES source("id")
)