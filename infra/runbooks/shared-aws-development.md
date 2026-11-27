# Shared AWS development

Phase 1.4 uses private PostgreSQL 17 on RDS, one EC2 Systems Manager tunnel node, a private S3 bucket, and a Cognito user pool in **Asia Pacific (Mumbai)** (`ap-south-1`). All developers share the `Estateflow` IAM profile (`estateflow-dev`), and the smoke checks run against the shared resources on the developer's machine (with a second machine optional if another teammate joins).

## Local passwords

Save EstateFlow setup and test passwords in `.env.rds-admin` at the repository root. Git ignores this file. It stores plain text, so keep it on your machine and put only the passwords you use in your copy. Use one `NAME=value` entry per line. Look up the specific entry you need when a console, database, or smoke check prompts for it.

| Entry | When to use it |
| --- | --- |
| `RDS_ADMIN_PASSWORD` | Sign in as the PostgreSQL administrator for database setup and administration. |
| `RDS_MIGRATOR_PASSWORD` | Sign in as `estateflow_migrator` to apply reviewed migrations. |
| `RDS_DEVELOPER_PASSWORD` | Sign in with your PostgreSQL developer login for the RDS smoke check. |
| `COGNITO_SMOKE_BUYER_PASSWORD` or `COGNITO_SMOKE_SELLER_PASSWORD` | Sign in as your assigned buyer or seller in the Cognito smoke check. |

Keep password values out of Markdown, screenshots, terminal output, and Git. AWS CLI session credentials stay in the named AWS profile.

## 1. Check the account and budget

1. Open **Billing and Cost Management → Free Tier** and check the plan, credit balance, and expiration. In the relevant service consoles, check which RDS and EC2 classes your account can launch on the current plan. Include database storage, backups, and any public IPv4 address for the tunnel in the estimate. Stay on the team's existing Free Plan. If the account blocks a required resource, record the restriction before proceeding. [AWS Free Tier tracking](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/tracking-free-tier-usage.html)
2. Select **Asia Pacific (Mumbai)** in the AWS console. Use the shared AWS account and the shared `Estateflow` IAM identity (`estateflow-dev` profile). If separate developer logins are added later, put them in an IAM user group with MFA enabled and scoped permissions. For a standalone Free Plan account, use the existing IAM path; joining AWS Organizations automatically upgrades the account to Paid. [AWS Free Plan terms](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html)
3. Install a current AWS CLI v2 and the Session Manager plugin locally. Sign in with the shared `estateflow-dev` profile. For IAM users using `aws login`, enable `SignInLocalDevelopmentAccess`. Verify the profile and inventory existing resources before creating anything. Reuse a resource if it matches this runbook and is already designated for EstateFlow. [AWS CLI sign-in](https://docs.aws.amazon.com/signin/latest/userguide/command-line-sign-in.html) · [Session Manager plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)

```powershell
$AwsProfile = "estateflow-dev"
$AwsRegion = "ap-south-1"
aws login --profile $AwsProfile --region $AwsRegion
aws sts get-caller-identity --profile $AwsProfile --region $AwsRegion
aws ec2 describe-vpcs --profile $AwsProfile --region $AwsRegion
aws ssm describe-instance-information --profile $AwsProfile --region $AwsRegion
aws rds describe-db-instances --profile $AwsProfile --region $AwsRegion
aws s3api list-buckets --profile $AwsProfile --region $AwsRegion
aws cognito-idp list-user-pools --max-results 60 --profile $AwsProfile --region $AwsRegion
```

Use an administrator's named profile for inventory if the developer identity lacks an inventory permission. Keep account-specific values in the team's setup notes.

## 2. Create the private database and tunnel in the console

1. In **VPC → Security groups**, create two groups in the selected VPC. For `estateflow-tunnel`, leave inbound rules empty and replace the default outbound rule with TCP 443 for the AWS APIs and TCP 5432 to `estateflow-db`. For `estateflow-db`, allow inbound PostgreSQL TCP 5432 from `estateflow-tunnel` only. Use a DB subnet group covering at least two Availability Zones in the same VPC. [RDS VPC and subnet groups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.WorkingWithRDSInstanceinaVPC.html)
2. In **IAM → Roles**, create an EC2 role with `AmazonSSMManagedInstanceCore`. In **EC2 → Launch instances**, choose an eligible small Amazon Linux instance with a current SSM Agent, the tunnel group, the IAM instance profile, and **IMDSv2 required**. With the default VPC, use one subnet with an internet gateway route and assign a public IPv4 address for outbound HTTPS. Keep the inbound group empty and omit SSH access. An existing private subnet with SSM API connectivity also works. Confirm the node is **Online** in **Systems Manager → Fleet Manager**. [SSM instance permissions](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-instance-profile.html) · [SSM network prerequisites](https://docs.aws.amazon.com/systems-manager/latest/userguide/setup-create-vpc.html)
3. In **RDS → Databases → Create database**, use **Full configuration**, **PostgreSQL 17**, a Single-AZ deployment, an eligible micro class, and the smallest eligible general-purpose storage setting. Set **DB instance identifier** to `estateflow-postgres-dev` and **Initial database name** to `estateflow_app`. Select the same VPC and the DB subnet group, set **Public access** to **No**, and attach only `estateflow-db`. Enable storage encryption. Save the master password under `RDS_ADMIN_PASSWORD` in [the local password file](#local-passwords).
4. Give teammates permission to start sessions on the specific node using `AWS-StartPortForwardingSessionToRemoteHost`, and to resume and terminate their own sessions. Limit session access to that document and node. Give the group `s3:GetObject` for the precise smoke fixture key from step 4 below. Use the provisioning identity to upload it. [Session Manager IAM examples](https://docs.aws.amazon.com/systems-manager/latest/userguide/getting-started-restrict-access-quickstart.html)

Verify the setup by CLI after provisioning. Check for an available, encrypted, Single-AZ PostgreSQL **17.x** instance with `Public: false`, the intended DB security group, and an **Online** agent at version **3.1.1374.0** or newer.

```powershell
$TunnelInstance = "<EC2 instance ID>"
aws ssm describe-instance-information --filters "Key=InstanceIds,Values=$TunnelInstance" --profile $AwsProfile --region $AwsRegion --query 'InstanceInformationList[].{Status:PingStatus,Agent:AgentVersion}'
aws rds describe-db-instances --db-instance-identifier estateflow-postgres-dev --profile $AwsProfile --region $AwsRegion --query 'DBInstances[0].{Status:DBInstanceStatus,Version:EngineVersion,Public:PubliclyAccessible,Encrypted:StorageEncrypted,MultiAZ:MultiAZ,Vpc:DBSubnetGroup.VpcId,Groups:VpcSecurityGroups[].VpcSecurityGroupId,Endpoint:Endpoint.Address}'
aws ec2 describe-security-groups --group-ids <tunnel-sg> <db-sg> --profile $AwsProfile --region $AwsRegion
```

## 3. Open the tunnel, bootstrap roles, and apply migrations

Copy the RDS endpoint from the CLI result or **RDS → Connectivity & security**. Start the tunnel in one terminal and leave it open. The local port is `15432`, separate from the disposable test DB port `55432`.

```powershell
$DbEndpoint = "<RDS endpoint>"
aws ssm start-session --profile $AwsProfile --region $AwsRegion --target $TunnelInstance --document-name AWS-StartPortForwardingSessionToRemoteHost --parameters "host=$DbEndpoint,portNumber=5432,localPortNumber=15432"
```

Install the [AWS RDS CA bundle](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html#UsingWithRDS.SSL.CertificatesAllRegions) locally. In a second terminal, from the repo root, set the same `$DbEndpoint` and set `$env:ESTATEFLOW_RDS_CA_FILE` to the absolute path of the bundle. On Docker Desktop 4.34 or later, enable **Settings → Resources → Network → Enable host networking** in Linux container mode. Linux Docker Engine supports this mode directly. The one-off Compose client reaches the tunnel over loopback. A native `psql` client can use the same connection parameters with `sslrootcert` set to the local bundle path. TLS verifies the actual RDS hostname via `host` while `hostaddr` connects to the local tunnel. [Docker host networking](https://docs.docker.com/engine/network/drivers/host/) · [PostgreSQL connection parameters](https://www.postgresql.org/docs/17/libpq-connect.html#LIBPQ-PARAMKEYWORDS)

```powershell
$RdsConnection = "host=$DbEndpoint hostaddr=127.0.0.1 port=15432 dbname=estateflow_app sslmode=verify-full sslrootcert=/rds-ca.pem"
docker compose -f infra/aws/compose.smoke.yaml run --rm rds-check "$RdsConnection user=<RDS administrator>"
```

Enter `RDS_ADMIN_PASSWORD` from `.env.rds-admin` at the password prompt. The owner runs the role bootstrap once on the verified RDS database. Create a dedicated login for migrations and one login per teammate in the same developer group. Use `psql`'s `\password <role>` to set an individual password for each login. Substitute the actual teammate role names and repeat the login setup for all teammates. Save each password you use under its key in [the local password file](#local-passwords).

```sql
CREATE ROLE estateflow_migrator LOGIN;
CREATE ROLE estateflow_developer NOLOGIN;
CREATE ROLE estateflow_dev_alex LOGIN IN ROLE estateflow_developer;
REVOKE CONNECT, TEMPORARY ON DATABASE estateflow_app FROM PUBLIC;
GRANT CONNECT, CREATE ON DATABASE estateflow_app TO estateflow_migrator;
GRANT CONNECT ON DATABASE estateflow_app TO estateflow_developer;
GRANT USAGE, CREATE ON SCHEMA public TO estateflow_migrator;
GRANT USAGE ON SCHEMA public TO estateflow_developer;
```

The designated migration operator confirms the reviewed Git revision and passing local and CI checks, agrees on a change window with teammates, and checks the RDS target and recovery option before applying the migration. The service-specific runtime roles belong to the phases that introduce database-backed operations.

From the repo root, activate the project virtual environment and install `project/requirements.txt`. In the second terminal, load the migration password from `.env.rds-admin` for Alembic. When the Compose client prompts separately, enter the same migration password.

```powershell
$MigrationPasswordEntry = @(Select-String -LiteralPath .env.rds-admin -Pattern '^RDS_MIGRATOR_PASSWORD=(.+)$')
if ($MigrationPasswordEntry.Count -ne 1) {
    throw "Set exactly one nonempty RDS_MIGRATOR_PASSWORD entry in .env.rds-admin."
}
$env:PGPASSWORD = $MigrationPasswordEntry[0].Matches[0].Groups[1].Value
Remove-Variable MigrationPasswordEntry
$env:PGSSLROOTCERT = $env:ESTATEFLOW_RDS_CA_FILE
$env:PGCONNECT_TIMEOUT = "10"
$env:ESTATEFLOW_DATABASE_URL = "postgresql+psycopg://estateflow_migrator@${DbEndpoint}:15432/estateflow_app?hostaddr=127.0.0.1&sslmode=verify-full"
docker compose -f infra/aws/compose.smoke.yaml run --rm rds-check "$RdsConnection user=estateflow_migrator" -c "SELECT current_database(), current_user, current_setting('server_version'), inet_server_addr();"
python -m alembic -c project/alembic.ini current
```

Confirm both preflight commands succeed and the target query reports the intended shared database and role. On a fresh database, `current` can have no revision to display. Apply the migration and check the head.

```powershell
python -m alembic -c project/alembic.ini upgrade head
python -m alembic -c project/alembic.ini current --check-heads
```

After the initial upgrade, expect `0001 (head)`. As `estateflow_migrator`, grant the developers permission to read the revision marker.

```powershell
docker compose -f infra/aws/compose.smoke.yaml run --rm rds-check "$RdsConnection user=estateflow_migrator" -c "GRANT SELECT ON public.alembic_version TO estateflow_developer;"
```

Clear the migration connection settings when finished. Keep the shared database free of the disposable listings fixture.

```powershell
Remove-Item Env:PGPASSWORD, Env:ESTATEFLOW_DATABASE_URL, Env:PGSSLROOTCERT, Env:PGCONNECT_TIMEOUT
```

## 4. Create the private bucket and upload the fixture

1. In **S3 → Buckets → Create bucket**, choose a globally unique EstateFlow development name in `ap-south-1`. Keep **Block all public access** enabled, **Bucket owner enforced** selected, and default S3-managed encryption enabled.
2. Upload one fictional or authorized JPEG as `smoke/estateflow-test-photo.jpg`. Record its SHA-256 from the original file and give each teammate scoped read permission for that key. [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)

```powershell
$Bucket = "<private EstateFlow development bucket>"
aws s3api get-public-access-block --bucket $Bucket --profile $AwsProfile --region $AwsRegion
aws s3api get-bucket-ownership-controls --bucket $Bucket --profile $AwsProfile --region $AwsRegion
aws s3api get-bucket-encryption --bucket $Bucket --profile $AwsProfile --region $AwsRegion
```

All four public-access-block settings should be `true`, object ownership should be `BucketOwnerEnforced`, and default encryption should be present.

## 5. Create the Cognito smoke client and identities

1. In **Cognito → User pools**, create or select the EstateFlow development pool. For a new pool, choose **Email** as the only sign-in identifier and **Single-page application** named `estateflow-dev-smoke` for the initial app client. After creation, disable **Self-service sign-up** under **Sign-up** so an administrator creates the test identities. Under **Domain**, use an AWS-provided Cognito prefix domain. Cognito Lite supports the classic hosted UI. [Cognito console setup](https://docs.aws.amazon.com/cognito/latest/developerguide/getting-started-user-pools-application.html) · [Cognito feature plans](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-sign-in-feature-plans.html)
2. Under **App clients**, use the dedicated public client without a client secret. Under **Login pages**, use the Cognito user pool as the identity provider, enable only **Authorization code grant** and the `openid` scope, and register exactly `http://127.0.0.1:8765/callback`. If the creation wizard asks for a return URL, use the same value. Use the browser on the machine running the smoke script so its callback reaches the local listener. The smoke tool uses PKCE. Phase 2 owns the Auth.js application client and its callback. [Cognito callback URL requirements](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_CreateUserPoolClient.html) · [Cognito PKCE](https://docs.aws.amazon.com/cognito/latest/developerguide/using-pkce-in-authorization-code.html)
3. In **Users**, create separate test identities for buyer and seller. Use team-controlled test addresses. Each teammate saves the password for their assigned identity in [the local password file](#local-passwords) and uses a fresh browser session to exercise that login.

```powershell
$PoolId = "<pool ID>"
$ClientId = "<public smoke client ID>"
aws cognito-idp describe-user-pool-client --user-pool-id $PoolId --client-id $ClientId --profile $AwsProfile --region $AwsRegion --query 'UserPoolClient.{Callbacks:CallbackURLs,Flows:AllowedOAuthFlows,Scopes:AllowedOAuthScopes,Providers:SupportedIdentityProviders,HasSecret:ClientSecret!=`null`}'
```

Expect the registered loopback callback, `code`, `openid`, `COGNITO`, and `HasSecret: false`.

## 6. Record the smoke checks

Open the tunnel, build the connection string from step 3, and download the fixture using the `estateflow-dev` AWS profile. At the PostgreSQL and Cognito prompts, use the developer and assigned test-user passwords from [the local password file](#local-passwords). (If a second teammate joins later, they can repeat these checks from their machine.)

```powershell
docker compose -f infra/aws/compose.smoke.yaml run --rm rds-check "$RdsConnection user=<personal PostgreSQL login>" -c "SELECT current_database(), current_user, current_setting('server_version'), inet_server_addr(), version_num FROM public.alembic_version;"

$CognitoDomain = "<prefix>.auth.ap-south-1.amazoncognito.com"
python infra/aws/cognito_smoke.py $CognitoDomain $ClientId

$PhotoPath = Join-Path ([IO.Path]::GetTempPath()) ("estateflow-" + [guid]::NewGuid() + ".jpg")
aws s3api get-object --bucket $Bucket --key smoke/estateflow-test-photo.jpg $PhotoPath --profile $AwsProfile --region $AwsRegion
if ($LASTEXITCODE -eq 0) { Get-FileHash -Algorithm SHA256 -LiteralPath $PhotoPath }
```

Expect PostgreSQL 17, `estateflow_app`, and revision `0001` from the agreed RDS instance. The Cognito tool reports success after code exchange and a userInfo response. Both photo hashes must match the owner's recorded hash. Close the tunnel after testing. In the [Phase 1.4 plan](../../Documentation/implementation/phase-01/phase1.4.md), record each teammate's outcome, migration revision, and date. Keep passwords, tokens, signed URLs, and private fixture values out of the evidence.
