ALTER TABLE "source" ADD "rolls" INTEGER;
UPDATE "source" SET "rolls" = 0;
ALTER TABLE "source" ADD "dice" INTEGER;
ALTER TABLE "source" ADD "natural" INTEGER;