CREATE TABLE IF NOT EXISTS "prefix" (
	"discord_id"            VARCHAR(255) NOT NULL UNIQUE,
	"prefix"                VARCHAR(255) NOT NULL,
	PRIMARY KEY("discord_id"),
	FOREIGN KEY("discord_id") REFERENCES source("discord_id")
);