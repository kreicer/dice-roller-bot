CREATE TABLE IF NOT EXISTS "source" (
	"id"	            INTEGER NOT NULL UNIQUE,
	"source_id"	        VARCHAR(255) NOT NULL UNIQUE,
	"type"	            INTEGER NOT NULL,
	"last_interation"	DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, "utc")),
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("type") REFERENCES source_types("id")
);