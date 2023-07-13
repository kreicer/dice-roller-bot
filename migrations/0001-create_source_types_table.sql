CREATE TABLE IF NOT EXISTS "source_types" (
	"id"	INTEGER UNIQUE NOT NULL,
	"type"	VARCHAR(255) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

INSERT INTO "source_types" ("type") VALUES
    ("guild")
    ("dm");