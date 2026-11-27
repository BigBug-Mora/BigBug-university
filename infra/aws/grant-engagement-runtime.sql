-- Run as the migration owner after Alembic has created account.accounts.
BEGIN;
GRANT USAGE ON SCHEMA account TO estateflow_engagement;
GRANT SELECT (id, cognito_issuer, cognito_subject, status),
      INSERT (id, cognito_issuer, cognito_subject)
ON account.accounts TO estateflow_engagement;
COMMIT;
