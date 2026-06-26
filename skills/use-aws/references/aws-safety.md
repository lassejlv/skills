# AWS Safety

Use this reference before write operations, IAM/security changes, billing-sensitive commands, production-facing changes, or commands with unclear side effects.

## Approval Gates

Proceed without extra approval only for clearly read-only commands that match the user's request. Ask for approval before commands that create, update, delete, start, stop, invoke, attach, detach, tag, untag, publish, deploy, rotate, grant, revoke, or change billing/cost exposure.

Before approval, state:

- AWS account ID and ARN from STS.
- Profile, region, and credential source if known.
- Exact resources and commands.
- Expected effect and whether it can cause downtime, access changes, data exposure, or cost.
- Verification and rollback plan.

Use this approval shape:

```text
please confirm apply <exact change> in AWS account <account-id> using profile <profile> in <region>
```

For broad deletion, account teardown, "nuke", "delete everything", or cleanup requests, stop using this skill and use `aws-account-cleanup`.

## Risk Classes

Read-only:

- `sts get-caller-identity`
- `list-*`, `describe-*`, `get-*`, `head-*`
- CloudWatch Logs queries and recent log tails without `--follow`
- Cost Explorer reads

Mutating:

- `create-*`, `update-*`, `put-*`, `modify-*`, `set-*`
- `start-*`, `stop-*`, `restart-*`, `reboot-*`
- `tag-*`, `untag-*`
- deployment commands, stack updates, ECS/Lambda config updates

Destructive:

- `delete-*`, `terminate-*`, `remove-*`, `empty`, `destroy`
- `detach-*`, `revoke-*`, policy removal, key deletion or scheduling deletion
- S3 object deletion, snapshot deletion, database deletion, IAM user/role/policy deletion

Cost-triggering or externally visible:

- Lambda invocation, ECS run task, Batch jobs, Step Functions executions
- Athena/Glue/EMR jobs, Bedrock/SageMaker calls, large S3 syncs
- Route 53, CloudFront, ACM, WAF, load balancer, security group, or public access changes

## Secrets

- Never print secret values from Secrets Manager, SSM SecureString, environment variables, credentials files, `.env`, private keys, or database URLs.
- If a task requires checking whether a secret exists, report metadata only: name, ARN, version label, last changed date, or policy.
- If a secret must be passed to a command, use process environment, stdin, or a temporary file with restrictive permissions and remove it after use.
- Do not paste AWS credentials into chat, commands, logs, or generated files.

## Ownership

Prefer changing the source of truth over manual console/CLI edits. Check for Terraform, CDK, Pulumi, Serverless, SAM, CloudFormation, Helm, GitHub Actions, Railway/Fly/Vercel deploy config, or repo scripts before editing AWS resources directly.

If ownership is unclear, inspect tags, CloudFormation stack membership, deployment history, and repo configuration before making changes.
