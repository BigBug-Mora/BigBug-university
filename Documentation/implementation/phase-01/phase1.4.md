# Phase 1.4 · Shared AWS development

Set up the documented shared dependencies so two teammates can reach the same private PostgreSQL database, use the Cognito user pool, and read the same authorized photo fixture. Application containers run on teammates’ machines in this phase. [Phase 1](phase1.md) · [Shared AWS development design](../../mvp/teach-stack/tech-stack.md#2-shared-aws-services-from-day-one) · [CI and shared AWS](../../mvp/ci/cd/ci.md#shared-aws-development)

## Console setup and CLI verification

The project owner makes AWS changes in the console using their administrator identity, with the agent guiding each step. Use an authenticated named AWS CLI profile for read-only verification. Start with `aws sts get-caller-identity --profile <profile>` to confirm the account and identity. Confirm the development region before checking regional resources. Inspect existing VPCs, RDS instances, Systems Manager managed nodes, S3 buckets, and Cognito user pools before creating anything.

After each console step, use the relevant CLI read operation to verify the setting and record the outcome here. Check the RDS engine version and public accessibility, Systems Manager managed-node status, S3 public access block, and Cognito callback URLs. Keep credentials and tokens in the local AWS sign-in flow. [AWS CLI sign-in](https://docs.aws.amazon.com/signin/latest/userguide/command-line-sign-in.html)

## Progress

- [ ] Check the selected account and region, provisioning access, remaining credits, and eligibility for the intended RDS, S3, Cognito, and tunnel resources. Record the selected PostgreSQL major version for [Phase 1.2](phase1.2.md). Reuse matching resources if the team already has them.
- [ ] Set up private RDS and the documented Systems Manager port-forwarding path. Confirm that application containers can reach the tunnel from local Compose and that each teammate uses their own AWS identity.
- [ ] Set up the shared Cognito pool with test users and local sign-in configuration. Use a focused sign-in smoke test. The product sign-in flow belongs to Phase 2.
- [ ] Set up the private S3 bucket and an authorized photo fixture. Verify team access with the AWS smoke test. The signed upload and gallery features belong to Phase 6.
- [ ] Write setup and verification steps in `infra/runbooks/`. Name the role responsible for applying reviewed shared migrations and document the explicit command, target verification, and coordination with teammates.
- [ ] After local and CI database checks pass, apply the reviewed initial migration to the shared development target through the documented procedure. Record the revision and who verified it.

## Acceptance check

From two teammates’ machines, open the private database tunnel and verify the same database and applied schema revision with read-only queries. Sign in with Cognito test identities and read the same authorized S3 fixture. Record which checks passed and the expected configuration each uses. Keep credentials, tokens, and signed URLs out of the runbook and test evidence.

## Decision log

- Use the shared AWS environment documented for development. Keep test fixtures disposable unless deliberately loading a named shared smoke-test fixture.
