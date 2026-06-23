---
name: aws-account-cleanup
description: Safely inventory and remove AWS account resources with mandatory dry-run-first discovery and explicit human confirmations. Use when the user asks to nuke, empty, clean up, delete everything in, or selectively remove resources from an AWS account, including destructive AWS cleanup, account teardown preparation, sandbox reset, or cost cleanup.
---

# AWS Account Cleanup

## Non-Negotiable Safety Flow

Treat this skill as destructive infrastructure work. Never delete, disable, detach, terminate, destroy, empty, or modify AWS resources until the required confirmations are complete.

1. Confirm access before touching AWS:
   - Ask the user exactly: `please confirm i have access to go through your aws account`
   - Do not run AWS commands before this confirmation, including read-only inventory commands.
2. Identify the active account and credentials after the user confirms:
   - Run `aws sts get-caller-identity`.
   - Report the account ID, ARN, and active AWS profile or environment source if detectable.
   - Stop if the identity does not clearly match the intended account.
3. Perform a dry run only:
   - Inventory resources across all enabled regions.
   - Prefer read-only `list`, `describe`, `get`, and tagging API calls.
   - Do not use commands with side effects, even if they have `--dry-run`, unless the command is strictly necessary to test delete permissions and cannot change state.
4. Summarize findings before deletion:
   - Group findings by service, region, and resource identifier.
   - Include obvious blockers such as termination protection, non-empty buckets, retained snapshots, protected log groups, service-linked roles, and root-account-only actions.
   - Ask the user to choose `all` or list exact resources, services, regions, or categories to remove.
5. Confirm deletion scope before deleting:
   - Ask exactly: `please confirm delete xxx from your xxx account`
   - Replace the first `xxx` with the precise deletion scope, such as `all discovered EC2 instances and unattached EBS volumes in eu-west-1`.
   - Replace the second `xxx` with the account ID or clearly identified account alias/profile.
   - Do not accept vague confirmation when the scope changed after the dry-run summary.
6. Delete only the confirmed scope:
   - Work in dependency order.
   - Re-check each target immediately before deletion.
   - Skip anything not present in the dry-run summary unless the user explicitly adds it and confirms the updated scope.
7. Verify and report:
   - Re-run read-only inventory for the confirmed scope.
   - Report deleted, skipped, failed, and still-present resources.
   - Include exact follow-up commands or console actions only for resources that could not be removed automatically.

## Dry-Run Inventory

Start with `aws sts get-caller-identity`, then enumerate regions:

```bash
aws ec2 describe-regions --all-regions --query 'Regions[?OptInStatus==`opt-in-not-required` || OptInStatus==`opted-in`].RegionName' --output text
```

For a broad cleanup, inspect common cost-bearing and dependency-heavy services first:

- EC2: instances, launch templates, AMIs owned by self, EBS volumes, snapshots, elastic IPs, NAT gateways, load balancers, target groups, security groups, key pairs.
- VPC: VPCs, subnets, route tables, internet gateways, egress-only gateways, NAT gateways, VPC endpoints, peering connections, network ACLs.
- S3: buckets, regions, versioning, object counts when feasible, lifecycle, replication, public access blocks.
- RDS and databases: DB instances, clusters, snapshots, subnet groups, parameter groups, option groups.
- ECS/EKS: clusters, services, tasks, node groups, Fargate profiles.
- Lambda and eventing: functions, layers, event source mappings, EventBridge rules and schedules.
- IAM: users, access keys, roles, policies, groups, instance profiles, OIDC/SAML providers. Treat IAM as global and high-risk.
- Logs and observability: CloudWatch log groups, alarms, dashboards, X-Ray groups.
- Secrets and config: Secrets Manager secrets, SSM parameters, AppConfig resources.
- DNS and edge: Route 53 hosted zones and records, CloudFront distributions, ACM certificates, WAF resources.
- Deployment services: CloudFormation stacks, Elastic Beanstalk apps, CodeBuild projects, CodePipeline pipelines.

Read `references/aws-inventory.md` when a concrete command checklist is useful.

## Deletion Order

Delete high-level orchestrators before their underlying resources when they own dependencies:

1. CloudFormation, CDK-managed stacks, Elastic Beanstalk, ECS services, EKS node groups, and other deployment managers.
2. Application front doors and compute: load balancers, target groups, ECS tasks/services, Lambda integrations, EC2 instances.
3. Network dependencies: NAT gateways, VPC endpoints, peering, internet gateways, subnets, route tables, security groups, VPCs.
4. Storage and databases: RDS instances/clusters, snapshots if confirmed, EBS volumes/snapshots, EFS file systems, S3 buckets after object and version cleanup.
5. Global services: CloudFront, Route 53, IAM, ACM us-east-1 certificates, WAF, global accelerator.
6. Logs, alarms, secrets, parameters, retained backups, and leftover service artifacts.

For `all`, interpret the request as all resources found in the dry run, not every possible AWS service. If new resources are discovered during deletion, pause, summarize them, and request a new confirmation.

## Refusal and Escalation Rules

- Refuse to proceed if the user asks to skip either confirmation phrase.
- Refuse to delete from an account that cannot be identified with `sts get-caller-identity`.
- Ask for a narrower scope when the dry-run results are too large or ambiguous to summarize precisely.
- Avoid closing the AWS account itself unless the user explicitly asks; account closure may require console/root actions and has billing, support, and organization side effects.
- Preserve evidence: keep command output summaries or saved inventory files if the user asks for an audit trail.
