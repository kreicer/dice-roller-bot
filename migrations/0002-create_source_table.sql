CREATE TABLE IF NOT EXISTS "source" (
	"discord_id"	    VARCHAR(255) NOT NULL UNIQUE,
	"type"	            INTEGER NOT NULL,
	"last_interation"	DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'utc')),
	PRIMARY KEY("discord_id"),
	FOREIGN KEY("type") REFERENCES source_type("id")
);