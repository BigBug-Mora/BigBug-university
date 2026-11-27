# Phase 1.4 · Shared AWS development

Set up the documented shared dependencies so two teammates can reach the same private PostgreSQL database, use the Cognito user pool, and read the same authorized photo fixture. Application containers run on teammates’ machines in this phase. [Phase 1](phase1.md) · [Shared AWS development design](../../mvp/teach-stack/tech-stack.md#2-shared-aws-services-from-day-one) · [CI and shared AWS](../../mvp/ci/cd/ci.md#shared-aws-development)

## Console setup and CLI verification

The project owner makes AWS changes in the console using their administrator identity, with the agent guiding each step. Use an authenticated named AWS CLI profile for read-only verification. Start with `aws sts get-caller-identity --profile <profile>` to confirm the account and identity. Confirm the development region before checking regional resources. Inspect existing VPCs, RDS instances, Systems Manager managed nodes, S3 buckets, and Cognito user pools before creating anything.

After each console step, use the relevant CLI read operation to verify the setting and record the outcome here. Check the RDS engine version and public accessibility, Systems Manager managed-node status, S3 public access block, and Cognito callback URLs. Keep AWS CLI session credentials and tokens in the local AWS sign-in flow. [AWS CLI sign-in](https://docs.aws.amazon.com/signin/latest/userguide/command-line-sign-in.html)

## Progress

- [x] Check the selected account and region, provisioning access, remaining credits, and eligibility for the intended RDS, S3, Cognito, and tunnel resources. Record the selected PostgreSQL major version for [Phase 1.2](phase1.2.md). Reuse matching resources if the team already has them.
- [x] Set up private RDS and the documented Systems Manager port-forwarding path. Confirmed that local Compose reaches the tunnel and verified the shared `Estateflow` IAM identity (`estateflow-dev` profile; single-IAM decision recorded below).
- [x] Set up the shared Cognito pool with test users and local sign-in configuration. Both identities passed the hosted sign-in smoke test on the owner's Windows machine. The product sign-in flow belongs to Phase 2.
- [x] Set up the private S3 bucket and an authorized photo fixture. Verified private bucket configuration and smoke-fixture download checksum using the shared `estateflow-dev` profile. The signed upload and gallery features belong to Phase 6.
- [x] Write the [AWS setup and verification runbook](../../../infra/runbooks/shared-aws-development.md). The designated migration operator uses `estateflow_migrator` after a target check and a coordinated change window.
- [x] After local and CI database checks pass, apply the reviewed initial migration to the shared development target through the documented procedure. Record the revision and who verified it.

## Acceptance check

Open the private database tunnel, verify the shared database and applied schema revision (`0001`) via local Compose, sign in with the Cognito buyer and seller test identities, and read the authorized S3 fixture with matching SHA-256. Originally scoped for two teammates’ machines; on 2026-11-27 the owner waived the separate second-teammate machine check and standardized on the single shared `Estateflow` IAM user. Record which checks passed and the expected configuration used. Keep credentials, tokens, and signed URLs out of the runbook and test evidence.

## Decision log

- **Single shared IAM identity and single-operator Phase 1.4 acceptance (2026-11-27):** Per the owner's decision, the team uses the single shared `Estateflow` IAM user (`estateflow-dev` CLI profile) instead of provisioning separate per-teammate IAM users, and the second-teammate machine check is waived for Phase 1.4. This updates [Phase 1](phase1.md) and the [Roadmap](../roadmap.md) Phase 01 acceptance criteria; the two distinct Cognito test identities (`buyer` and `seller`) remain active for multi-role workflow testing in later phases (including Phase 15).

- Store setup and test passwords in the Git-ignored `.env.rds-admin` file. Use the [runbook's password keys](../../../infra/runbooks/shared-aws-development.md#local-passwords) to find the right entry for database setup, migration, or sign-in.
- Use the shared AWS environment documented for development. Keep test fixtures disposable unless deliberately loading a named shared smoke-test fixture.
- Use PostgreSQL 17 to match the [Phase 1.2 disposable checks](phase1.2.md#verification-and-ci-handoff). Target `ap-south-1` (Mumbai) for shared development following the owner's region correction. Keep all four AWS dependencies in Mumbai and confirm Free Plan eligibility before provisioning.
- Use one AWS account for the team and personal IAM sign-ins with group-based access. Use an administrator identity for provisioning and scoped access for daily development checks.
- Use a separate private EstateFlow bucket. The existing bucket has a public bucket policy and all four public-access blocks are off.
- Use a one-off Compose PostgreSQL client with host networking to verify access to the loopback tunnel. Use full RDS hostname validation with `hostaddr` pointing at the tunnel. Keep migration and developer accounts separate.
- Use a dedicated public Cognito app client for the PKCE smoke check. Phase 2 owns the Auth.js client.

## Verification and owner handoff

- On 2026-11-26, read-only AWS CLI inventory verified the account identity. In `us-east-1` it found a default VPC and no RDS instances, active EC2 instances, SSM managed nodes, or Cognito user pools. The existing S3 bucket is public by policy. The inventoried CLI profile resolved to the account root identity. The owner still needs to confirm the billing balance and eligibility and set up individual development identities.
- A follow-up read-only inventory in Mumbai found an available default VPC and no RDS instances, SSM managed nodes, or Cognito user pools. RDS listed PostgreSQL 17 for `db.t4g.micro` in Mumbai. The service catalog confirms regional availability. The owner still needs to confirm eligibility under the account's Free Plan.
- The Compose smoke client queried disposable PostgreSQL 17.12 over loopback port `15432`. The runbook's role setup let `estateflow_migrator` apply revision `0001` and a developer login read the revision marker. The Property service test passed.
- The Cognito tool accepted a matching callback state after rejecting an incorrect state, then performed the expected PKCE token exchange and userInfo request against simulated Cognito responses. The live Cognito and S3 checks remain open.

### AWS checkpoint on 2026-11-27

| Item | Last observed |
| --- | --- |
| Local tooling | Windows AWS CLI `2.37.12`; Session Manager plugin `1.2.896.0`. The named profile `estateflow-dev` authenticated as the Estateflow IAM user in Mumbai (`ap-south-1`). |
| EC2 tunnel node | `estateflow-tunnel`, `t3.micro`, Amazon Linux 2023, using IAM role `estateflow-ec2-ssm` and security group `estateflow-tunnel`. Systems Manager reported **Online** with agent version `3.3.5828.0`. |
| RDS | `estateflow-postgres-dev`, database `estateflow_app`, PostgreSQL `17.12`, `db.t4g.micro`, Single-AZ. AWS reported **Available**, private, and encrypted. The console setup selected `estateflow-db` for access from the tunnel node. |
| Live tunnel check | Local `127.0.0.1:15432` forwarded to port `5432` on RDS. A native PostgreSQL client signed in as `postgres`, ran a read-only query, and verified the RDS hostname and TLS. Docker Desktop was stopped, so the live Compose check remains open. |

#### Step 3 continuation on 2026-11-27

- STS verified the `estateflow-dev` IAM identity in Mumbai. Systems Manager reported the tunnel node Online and the previous port-forwarding session Connected. The Session Manager plugin was still listening on laptop loopback port `15432`, so the existing session was reused. AWS reported RDS Available, private, and encrypted, with PostgreSQL 17.12 on RDS port `5432`, one day of backup retention, and a latest restorable time.
- A native PostgreSQL client used the AWS Mumbai CA bundle and full hostname verification through that tunnel. The admin query returned `estateflow_app`, PostgreSQL 17.12, and active TLS. The public schema had no tables, and no EstateFlow roles existed before bootstrap.
- Created the `estateflow_migrator` login, `estateflow_developer` group, and owner's `estateflow_dev_estateflow` login with the runbook grants. Both logins authenticated over verified TLS. The migrator could create objects in the public schema and the developer could not. The two password entries are stored in the ignored local password file. Additional teammate logins still need setup.
- `alembic current` succeeded as `estateflow_migrator` and returned no revision. The migration files and configuration match the checked-out merge commit `0208243`. Phase 1.3 records passing local and CI checks. The team's migration window still needs confirmation. Revision `0001` and the developer grant on its revision marker are pending. No disposable listing fixtures were loaded.
- The Docker engine was running, but the live Compose client received connection refused at laptop loopback port `15432` while the native tunnel was still listening. Resume by checking **Docker Desktop → Settings → Resources → Network → Enable host networking**, then rerun the Compose preflight before applying the migration.
- AWS inventory found only the previously identified S3 bucket and no Cognito pools in Mumbai under the named profile. The dedicated private S3 bucket and fixture, Cognito setup, and independent checks from two teammates remain open.
- On the next retry, STS verified the same named IAM identity. Systems Manager reported no active sessions and Windows had no listener on laptop port `15432`. Reopened the tunnel using the installed Session Manager plugin by adding its installation directory to the command's PATH. The plugin reported that laptop port `15432` opened. Docker was running, but the Compose retry still received connection refused. The Docker Desktop host networking setting and the team's migration window still need confirmation.
- After the owner enabled Docker Desktop host networking, Systems Manager reported the tunnel Connected and Windows was listening on laptop port `15432`. The live Compose `rds-check` query passed with full RDS hostname verification. The query returned `estateflow_app`, `estateflow_migrator`, PostgreSQL 17.12, and active TLS. Resume by confirming the team's migration window and rechecking the target before applying revision `0001`.

#### Migration preflight recheck on 2026-11-27

- The `estateflow-dev` profile resolved to the Estateflow IAM user. Systems Manager reported the node Online and the existing port-forwarding session Connected. The Windows Session Manager plugin owned the listener at `127.0.0.1:15432`, so the tunnel was reused.
- AWS reported `estateflow-postgres-dev` available, private, encrypted, and Single-AZ in Mumbai, with one day of automated backup retention and a latest restorable time. The live Compose check reached `estateflow_app` as `estateflow_migrator` with full hostname verification and active TLS on RDS port `5432`. The query found no `public.alembic_version` table, and `alembic current` succeeded without an applied revision.
- The migration files and pinned requirements matched reviewed commit `0208243`, and `alembic heads` reported `0001 (head)`. The migration and developer revision grant are awaiting the owner's confirmation of the team's window.
- Fresh inventory found only the unrelated S3 bucket and no Cognito pools in Mumbai. The owner still needs to provision the dedicated S3 bucket and Cognito resources, and two teammates still need to run their independent checks.

#### Shared migration on 2026-11-27

- The owner confirmed the team's migration window. The operator rechecked the shared RDS target and its latest restorable time at 08:39 Colombo time, then reused the verified tunnel from laptop port `15432` to RDS port `5432`. The Compose preflight confirmed PostgreSQL 17.12 with full TLS hostname verification and found neither the revision table nor the four application schemas.
- The operator applied the reviewed `0208243` migration with `alembic upgrade head` as `estateflow_migrator`. The follow-up `alembic current --check-heads` reported `0001 (head)`. No disposable listings were loaded.
- As `estateflow_migrator`, the operator granted `estateflow_developer` SELECT on `public.alembic_version`. The live Compose query as the owner's `estateflow_dev_estateflow` login returned revision `0001` over verified TLS and confirmed that the login lacks CREATE on the `public` schema. Additional teammate logins and independent checks remain open.
- The AWS Free Tier API reported an active Free Plan with credits remaining and a plan expiration on 2027-03-28 Colombo time. The next owner console action is to create the dedicated private S3 bucket in Mumbai.

#### S3 bucket verification on 2026-11-27

- The owner created the general purpose bucket `estateflow-dev-photos-bigbug-mumbai` in the AWS console. The `estateflow-dev` CLI profile verified location `ap-south-1`, all four Block Public Access flags enabled, `BucketOwnerEnforced` ownership, and default SSE-S3 encryption (`AES256`).
- Generated a synthetic 320 × 200 JPEG and uploaded it as `smoke/estateflow-test-photo.jpg` with the `estateflow-dev` CLI profile. S3 reported `image/jpeg`, 4,987 bytes, and SSE-S3 (`AES256`). The downloaded file matched the original and the S3 checksum. SHA-256 in hex is `F4400B2C54B21FFC3D614DCAD49E1F7050AA9136B69FDF80D4F7F5E47D540AB5`. Independent access verification remains open.

#### Cognito setup checkpoint on 2026-11-27

- A read-only `list-user-pools` check with the `estateflow-dev` profile returned an empty list in Mumbai. The owner can create the pool and its initial `estateflow-dev-smoke` app client in the console.
- The smoke script uses `http://127.0.0.1:8765/callback` for both authorization and token exchange. AWS documents support for this HTTP loopback host and custom ports. Verify the registered value through `describe-user-pool-client` and exercise it in a live sign-in. [Cognito callback URL requirements](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_CreateUserPoolClient.html)
- After the owner created the pool and its `estateflow-dev-smoke` client, `describe-user-pool` verified email-only sign-in on Essentials, and `describe-user-pool-domain` reported the AWS-provided domain active with managed login. Essentials supports the active sign-in page and is suitable for this smoke check.
- `describe-user-pool-client` confirmed the exact configured callback `http://127.0.0.1:8765/callback`, authorization-code grant, the Cognito pool as identity provider, and no client secret. The initial scopes were `email`, `phone`, and `openid`.
- The owner disabled self-registration in the console. `describe-user-pool` returned `AllowAdminCreateUserOnly: true`.
- After the owner saved the login page settings, `describe-user-pool-client` reported `openid` as the only scope and reconfirmed the exact callback, authorization-code grant, Cognito identity provider, and absence of a client secret. `list-users` returned an empty list before the owner began creating the buyer and seller test identities. The live sign-in check is pending.
- At the owner's request, the `estateflow-dev` CLI profile created the buyer and seller test identities with invitations suppressed. `admin-get-user` initially reported both accounts as enabled and in `FORCE_CHANGE_PASSWORD`.
- The CLI then set the generated passwords as permanent and verified both identities in `CONFIRMED` status. The sign-in addresses and current passwords are in the Git-ignored local password file. Live `USER_AUTH` API sign-in matched each account's distinct Cognito subject, and the check revoked both refresh tokens.
- A request to `/oauth2/authorize` with `openid`, S256 PKCE, and `http://127.0.0.1:8765/callback` returned a redirect to hosted login with the callback intact.
- The buyer and seller each completed a fresh hosted sign-in on the owner's Windows machine. Both runs of `infra/aws/cognito_smoke.py` received the loopback callback, exchanged the code with S256 PKCE, verified that `userInfo` returned a subject, and exited successfully.

#### Single-operator acceptance checkpoint on 2026-11-27

- Per the owner's decision, the team uses the single shared `Estateflow` IAM user (`estateflow-dev` CLI profile) rather than separate per-teammate IAM accounts, and the second-teammate machine verification is waived.
- Read-only AWS CLI checks with `estateflow-dev` in `ap-south-1` reconfirmed the `Estateflow` IAM identity, `estateflow-postgres-dev` (`available`, PostgreSQL `17.12`, private, encrypted), and SSM tunnel node `i-0f6992ac7c30c5d47` (`Online`, agent `3.3.5828.0`).
- With RDS (`0001` via Compose `rds-check` as `estateflow_dev_estateflow`), S3 (`estateflow-dev-photos-bigbug-mumbai` fixture download matching SHA-256), and Cognito (buyer and seller PKCE sign-ins via `cognito_smoke.py`) all passing on the owner's machine, Phase 1.4 is accepted.
