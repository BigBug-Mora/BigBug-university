BEGIN;
CREATE ROLE estateflow_property LOGIN;
SELECT format('GRANT CONNECT ON DATABASE %I TO estateflow_property', current_database())
\gexec
COMMIT;
