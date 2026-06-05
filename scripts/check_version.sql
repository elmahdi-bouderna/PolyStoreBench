SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name ILIKE 'version';
SELECT * FROM "VERSION" LIMIT 5;
