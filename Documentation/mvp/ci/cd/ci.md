# EstateFlow AI MVP Continuous Integration

Use GitHub Actions for CI while the team runs the application locally against shared AWS services. Deploy the hosted demo manually. Revisit automated deployment if releases become frequent or the manual procedure becomes error-prone.

## GitHub Actions workflow

Add `.github/workflows/ci.yml` when the first versioned migration is ready. Run it on pull requests and pushes to `main`. Require the implemented CI checks before merging to `main`.

1. **Start with the database migration check.** Start a disposable PostgreSQL instance on the runner using the same major version as RDS. Apply the committed migrations to an empty database and load fictional fixtures for integration tests. Once a demo release exists, also test upgrading from its schema with sample records and verify that the records survive.
2. **Add application checks as the code lands.** Install declared dependencies and run backend lint and unit tests, plus frontend lint, TypeScript checks, and tests as they become available.
3. **Test the seller-to-buyer workflow through the API.** Use test identities and mocked model responses. Verify that two buyers asking about the same missing property fact create one seller inquiry group, that the approved answer reaches both eligible conversations, and that private details are visible only to buyers with a grant.
4. **Verify packaging and startup.** Build the application images once Dockerfiles exist. When Compose is ready, start the stack and check that the frontend and API respond. Add RabbitMQ and a worker smoke test when background jobs are implemented.

## Shared AWS development

Provision private RDS PostgreSQL, S3, and Cognito first. Developers run the application locally in Docker Compose and use an AWS Systems Manager tunnel to reach RDS. A teammate applies reviewed migrations to the shared database as an explicit step. CI uses its own temporary PostgreSQL instance and test fixtures, so it runs without AWS credentials or live model calls.

## Manual hosted demo release

Deploy a specific Git revision. Apply pending migrations once, start the application containers, and smoke-test the hosted URL. Verify sign-in, listing publication, and delivery of an approved seller answer to the eligible buyer. If local development and the hosted app share the same database, coordinate one migration for both. If they use separate databases, apply and track migrations for each database.

See the [MVP technology stack](../../teach-stack/tech-stack.md) for the shared AWS setup and the [database contracts](../../database/contracts.md) for workflow behavior and permissions.
