---
name: use-aws
description: Operate and investigate AWS accounts safely through AWS CLI and profile-aware workflows. Use when Codex needs to inspect AWS account identity, profiles, regions, costs, logs, deployments, IAM, S3, EC2, RDS, Lambda, ECS, CloudWatch, Route 53, CloudFormation, or make scoped non-destructive AWS changes. For broad cleanup, nuking, deleting everything, account teardown, or destructive resource removal, use aws-account-cleanup instead.
---

# Use AWS

## Core Workflow

1. Classify the request before touching AWS:
   - Read-only: identity checks, lists, describes, logs, billing summaries, config inspection.
   - Mutating but reversible: tagging, scaling, updating config, creating scoped resources.
   - Destructive or cleanup: deleting, terminating, emptying buckets, detaching policies, removing resources. Use `aws-account-cleanup` for broad cleanup or teardown.
2. Establish account context:
   - Prefer an explicitly provided profile and region.
   - If none is provided, run `scripts/aws-context.sh` from this skill to inspect local AWS CLI context.
   - Report account ID, ARN, profile, and region before changing anything.
3. Use read-only commands first:
   - Prefer `list`, `describe`, `get`, `head`, and CloudWatch event/log inspection.
   - Use `--profile`, `--region`, `--output json`, and narrow `--query` expressions.
   - Save large raw outputs under the current workspace `work/` directory when useful.
4. Before mutating anything:
   - Read `references/aws-safety.md`.
   - Summarize the exact account, profile, region, resources, commands, expected effect, and rollback path.
   - Ask for explicit approval unless the user already approved the exact command and scope.
5. After changes:
   - Verify with read-only commands.
   - Report what changed, what was skipped, and any residual risk.

## Helper Script

Use the read-only context helper when starting AWS work or when account/profile/region is ambiguous:

```bash
/Users/lassevestergaard/.codex/skills/use-aws/scripts/aws-context.sh
/Users/lassevestergaard/.codex/skills/use-aws/scripts/aws-context.sh --profile my-profile --region eu-west-1
/Users/lassevestergaard/.codex/skills/use-aws/scripts/aws-context.sh --all-profiles
```

The script prints AWS CLI availability, relevant environment variable status with secret values hidden, configured profile names, region resolution, and `sts get-caller-identity` output. It never creates, updates, or deletes AWS resources.

## References

- Read `references/aws-cli-patterns.md` when building AWS CLI commands, checking services, gathering logs, or troubleshooting deployments.
- Read `references/aws-safety.md` before any write operation, IAM/security change, billing-sensitive operation, production-facing change, or command whose side effects are unclear.

## Operating Rules

- Never print AWS secrets, access keys, session tokens, private keys, database passwords, or secret values. Redact instead.
- Treat account ID, ARN, profile, region, resource identifiers, tags, and log excerpts as okay to report unless the user asks otherwise.
- Prefer infrastructure-as-code ownership when a repo contains Terraform, CDK, Pulumi, Serverless, SAM, or CloudFormation. Inspect the owning code before manual AWS changes.
- Do not assume the default profile is safe. Resolve identity every session and whenever credentials, profile, or region changes.
- Do not run long-lived commands such as `logs tail --follow`, SSM sessions, port forwards, deploy watches, or interactive auth without making the runtime behavior clear to the user.
