-- Docker bootstrap runs this only for the disposable instance.
CREATE ROLE estateflow_migrator LOGIN PASSWORD 'disposable-migration';
ALTER DATABASE estateflow_test OWNER TO estateflow_migrator;
