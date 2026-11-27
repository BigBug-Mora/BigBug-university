-- Run as the database administrator on the intended database.
BEGIN;
CREATE ROLE estateflow_engagement LOGIN;
SELECT format('GRANT CONNECT ON DATABASE %I TO estateflow_engagement', current_database())
\gexec
COMMIT;
