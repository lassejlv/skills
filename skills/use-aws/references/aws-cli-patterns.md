# AWS CLI Patterns

Use explicit profile and region arguments whenever possible:

```bash
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" sts get-caller-identity --output json
```

Prefer JSON output for data that Codex will parse, and use `--query` to keep output small. Save large outputs under the current workspace `work/` directory and summarize them instead of pasting pages of JSON.

## Context

```bash
aws configure list-profiles
aws --profile "$AWS_PROFILE_NAME" sts get-caller-identity --output json
aws --profile "$AWS_PROFILE_NAME" iam list-account-aliases --output json
aws --profile "$AWS_PROFILE_NAME" ec2 describe-regions --all-regions \
  --query 'Regions[?OptInStatus==`opt-in-not-required` || OptInStatus==`opted-in`].RegionName' \
  --output text
```

If AWS SSO credentials are expired, run `aws sso login --profile <profile>` only when the user expects an interactive browser login.

## Cost And Billing

Cost Explorer is global and usually queried from `us-east-1`. Compute dates dynamically from the current date.

```bash
aws --profile "$AWS_PROFILE_NAME" ce get-cost-and-usage \
  --time-period Start="$START_DATE",End="$END_DATE" \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output json
```

For cost investigations, correlate Cost Explorer with regional inventories for EC2, NAT gateways, EBS, RDS, load balancers, logs, snapshots, S3 storage, and data transfer.

## Common Read-Only Checks

S3:

```bash
aws --profile "$AWS_PROFILE_NAME" s3api list-buckets --output json
aws --profile "$AWS_PROFILE_NAME" s3api get-bucket-location --bucket "$BUCKET" --output json
aws --profile "$AWS_PROFILE_NAME" s3api get-public-access-block --bucket "$BUCKET" --output json
```

EC2 and VPC:

```bash
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" ec2 describe-instances --output json
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" ec2 describe-volumes --output json
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" ec2 describe-nat-gateways --output json
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" ec2 describe-security-groups --output json
```

RDS:

```bash
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" rds describe-db-instances --output json
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" rds describe-db-clusters --output json
```

Lambda:

```bash
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" lambda list-functions --output json
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" lambda get-function-configuration --function-name "$FUNCTION" --output json
```

ECS:

```bash
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" ecs list-clusters --output json
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" ecs list-services --cluster "$CLUSTER" --output json
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" --output json
```

CloudFormation:

```bash
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE UPDATE_ROLLBACK_COMPLETE ROLLBACK_COMPLETE \
  --output json
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" cloudformation describe-stack-events --stack-name "$STACK" --output json
```

Logs:

```bash
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" logs describe-log-groups --output json
aws --profile "$AWS_PROFILE_NAME" --region "$AWS_REGION_NAME" logs tail "$LOG_GROUP" --since 1h
```

IAM:

```bash
aws --profile "$AWS_PROFILE_NAME" iam get-account-summary --output json
aws --profile "$AWS_PROFILE_NAME" iam list-users --output json
aws --profile "$AWS_PROFILE_NAME" iam list-roles --output json
aws --profile "$AWS_PROFILE_NAME" iam list-policies --scope Local --output json
```

Route 53 and CloudFront:

```bash
aws --profile "$AWS_PROFILE_NAME" route53 list-hosted-zones --output json
aws --profile "$AWS_PROFILE_NAME" cloudfront list-distributions --output json
```

## Troubleshooting Flow

1. Resolve the AWS account, profile, region, and resource identifiers.
2. Find the owner: tags, CloudFormation stack, CDK/Terraform state, deployment pipeline, or repo config.
3. Pull recent events before logs: CloudFormation events, ECS service events, Lambda last update status, ELB target health, RDS events.
4. Pull focused logs for the smallest useful time window.
5. Form a hypothesis and verify it with read-only commands.
6. For fixes, switch to `references/aws-safety.md` and get approval before changing state.
