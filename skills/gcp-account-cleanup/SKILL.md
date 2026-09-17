---
name: gcp-account-cleanup
description: Safely inventory and remove Google Cloud project resources with mandatory dry-run-first discovery and explicit human confirmations. Use when the user asks to nuke, empty, clean up, delete everything in, or selectively remove resources from Google Cloud projects, including teardown preparation, sandbox reset, and cost cleanup.
---

# Google Cloud Account Cleanup

## Non-Negotiable Safety Flow

Treat this skill as destructive infrastructure work. Google Cloud resources normally belong to **projects**; a Google identity, organization, folder, and billing account are different scopes. Never delete, disable, detach, stop, destroy, empty, or modify resources until the required confirmations are complete.

1. Confirm access before touching Google Cloud:
   - Ask the user exactly: `please confirm i have access to go through your google cloud projects`
   - Do not run Google Cloud commands before this confirmation, including read-only inventory commands.
2. Identify the active identity and intended project scope after the user confirms:
   - Run `gcloud auth list --filter=status:ACTIVE`, `gcloud config list`, and `gcloud config configurations list`. Check for service account impersonation and credential or project overrides in the environment without printing secrets or tokens.
   - Run `gcloud projects describe PROJECT_ID` for each intended project and report its project ID, project number, lifecycle state, active principal, and configuration or impersonation source if detectable.
   - If the project is unknown, `gcloud projects list` can show accessible candidates; ask the user to choose exact project IDs before inventorying resources. Accessible projects are not automatically authorized deletion targets.
   - Stop if the principal or project does not clearly match the user's intended scope.
3. Perform a dry run only:
   - Inventory the selected project IDs across relevant global, regional, and zonal locations. Use read-only `list`, `describe`, `get`, and Cloud Asset Inventory search calls. Pass `--project=PROJECT_ID` explicitly where supported; do not rely on a changing active project.
   - Cloud Asset Inventory can help discover resources but may be unavailable, permission-limited, or incomplete for a service. Cross-check important services with their own read-only list calls. Treat permission errors as unknown coverage, never as an empty project.
   - Do not enable APIs, grant roles, alter configuration, or use side-effecting commands as part of a dry run. Avoid `--quiet` on any future destructive command.
4. Summarize findings before deletion:
   - Group by project ID, service, location, and resource identifier. Identify ownership and dependencies where possible.
   - Include blockers such as deletion protection, retention or holds, non-empty or versioned buckets, final backups and snapshots, shared VPC or organization dependencies, and insufficient permissions.
   - Ask the user to choose `all` or exact resources, services, locations, or categories within named projects. If coverage is incomplete, identify the unscanned areas explicitly.
5. Confirm deletion scope before deleting:
   - Ask exactly: `please confirm delete xxx from your xxx google cloud project`
   - Replace the first `xxx` with the precise discovered deletion scope, such as `the listed Compute Engine instances and unattached disks in europe-west1-b`. Replace the second `xxx` with the exact project ID. For multiple projects, ask a separate confirmation for each project.
   - Do not accept vague confirmation when the scope changed after the dry-run summary.
6. Delete only the confirmed scope:
   - Work in dependency order and re-check each target and project ID immediately before deletion.
   - Skip anything absent from the dry-run summary unless the user explicitly adds it and confirms the updated scope. Never silently follow dependencies into another project, folder, or organization.
7. Verify and report:
   - Re-run read-only inventory for the confirmed scope. Report deleted, skipped, failed, and still-present resources, including operations still in progress.
   - Give exact follow-up commands or console actions only for resources that could not be removed automatically.

## Dry-Run Inventory

After access confirmation, establish identity and exact project IDs. For a broad cleanup, use Cloud Asset Inventory as a discovery aid:

```bash
gcloud asset search-all-resources --scope="projects/PROJECT_ID" --format=json
```

The search requires `cloudasset.assets.searchAllResources` permission. Do not enable the API merely to run inventory. Inspect common cost-bearing and dependency-heavy services directly:

- Compute Engine: instances, instance groups and templates, disks, snapshots, images, reserved addresses, forwarding rules, load balancers, and GPUs.
- Networking: VPC networks, subnets, firewall rules, routers and Cloud NAT, VPNs, interconnect attachments, private service connections, DNS zones, and shared VPC attachments.
- Storage and databases: Cloud Storage buckets and object versions, Cloud SQL instances and backups, Filestore, Bigtable, Spanner, Firestore, and database exports.
- Managed compute: GKE clusters and node pools, Cloud Run services and jobs, Cloud Functions, App Engine, and VM fleets owned by higher-level controllers.
- Messaging and integration: Pub/Sub, Eventarc, Cloud Scheduler, Cloud Tasks, and Workflows.
- Platform and security: Artifact Registry, Secret Manager, service accounts and keys, project IAM bindings, KMS keys, logging sinks, and monitoring alerting policies.
- Project administration: enabled APIs, project liens, billing linkage, and organization policies as context. Do not treat disabling APIs, changing billing, or deleting a project as routine resource cleanup.

Read [references/gcp-inventory.md](references/gcp-inventory.md) when a concrete command checklist is useful.

## Deletion Order

Remove resources in dependency order, accounting for their actual owner:

1. Deployment managers and controllers, such as Terraform-managed stacks when the state and authorization are available, GKE workloads and node pools, managed instance groups, and App Engine or Cloud Run services that recreate dependencies.
2. Application front doors and compute: load balancers and forwarding rules, serverless integrations, VMs, clusters, and jobs.
3. Network dependencies: VPNs and private connections, Cloud NAT and routers, firewall rules, subnets, then networks. Check shared VPC consumers in other projects.
4. Storage and databases: instances, backups and snapshots if confirmed, disks, file stores, registries, then buckets after objects and versions are accounted for.
5. DNS, Pub/Sub and eventing, secrets and keys, logs and monitoring artifacts, service accounts and IAM bindings last to preserve access for verification.

For `all`, interpret the request as the resources found in the dry run **within the confirmed project IDs**, not every possible Google Cloud service. If new resources are discovered during deletion, pause, summarize them, and request a new confirmation.

## Refusal and Escalation Rules

- Refuse to proceed if the user asks to skip either confirmation phrase.
- Refuse to delete from a project whose ID and active principal cannot be identified.
- Ask for a narrower scope when the dry-run results are too large or ambiguous to summarize precisely.
- Project deletion is a separate action: do it only when explicitly requested, after inventorying project contents and obtaining a distinct confirmation naming the exact project ID. Do not delete folders, organizations, or close billing accounts under this skill without an explicit request and separate scope review.
- Preserve command output summaries or saved inventory files if the user asks for an audit trail. Never store access tokens or private keys in the audit trail.
