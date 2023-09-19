CREATE TABLE IF NOT EXISTS "source_type" (
	"id"	INTEGER UNIQUE NOT NULL,
	"type"	VARCHAR(255) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

INSERT INTO "source_type" ("type") VALUES
    ("guild"),
    ("dm");