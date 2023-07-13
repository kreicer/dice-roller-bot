CREATE TABLE IF NOT EXISTS "schema_history" (
    "applied_version" INTEGER NOT NULL
);

INSERT INTO "schema_history" ("applied_version") VALUES (0);