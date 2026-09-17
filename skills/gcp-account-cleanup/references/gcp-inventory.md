# Google Cloud Inventory Checklist

Use this reference only after the required access confirmation. Keep every dry-run command read-only. Replace `PROJECT_ID` with an exact project ID chosen by the user; do not copy commands with a placeholder into a shell.

## Identity and Project

```bash
gcloud auth list --filter=status:ACTIVE
gcloud config list
gcloud config configurations list
gcloud projects list
gcloud projects describe PROJECT_ID --format=json
```

`gcloud auth list` and active configuration do not by themselves prove which principal an impersonated request uses. Check `auth/impersonate_service_account` and relevant `CLOUDSDK_*` overrides without printing credentials.

## Project-Wide Discovery

```bash
gcloud asset search-all-resources --scope="projects/PROJECT_ID" --format=json
```

Cloud Asset Inventory requires permission and service availability. Failure or an empty result does not prove that all services are empty. Keep command errors in the inventory summary. For organization or folder cleanup, get separate scope authorization and use the corresponding `organizations/NUMBER` or `folders/NUMBER` scope; do not infer it from a project request.

## Direct Service Checks

Run only checks relevant to the selected project and enabled services. Prefer explicit `--project=PROJECT_ID`. Some services need a location-specific list or describe call to capture full coverage.

```bash
gcloud compute instances list --project=PROJECT_ID --format=json
gcloud compute disks list --project=PROJECT_ID --format=json
gcloud compute snapshots list --project=PROJECT_ID --format=json
gcloud compute addresses list --project=PROJECT_ID --format=json
gcloud compute forwarding-rules list --project=PROJECT_ID --format=json
gcloud compute networks list --project=PROJECT_ID --format=json
gcloud compute subnetworks list --project=PROJECT_ID --format=json
gcloud compute firewalls list --project=PROJECT_ID --format=json
gcloud sql instances list --project=PROJECT_ID --format=json
gcloud container clusters list --project=PROJECT_ID --format=json
gcloud storage buckets list --project=PROJECT_ID --format=json
gcloud artifacts repositories list --project=PROJECT_ID --location=all --format=json
gcloud secrets list --project=PROJECT_ID --format=json
gcloud iam service-accounts list --project=PROJECT_ID --format=json
gcloud projects get-iam-policy PROJECT_ID --format=json
```

Check Cloud Run, Cloud Functions, App Engine, Pub/Sub, Cloud Scheduler, Eventarc, Cloud Tasks, Cloud DNS, KMS, Filestore, Bigtable, Spanner, Firestore, Logging, and Monitoring according to the services in use. Use current service-specific CLI documentation to choose exact location flags. For buckets, inspect object and version counts, retention policies, and holds before proposing deletion. For databases, inspect backups and deletion protection.

## Summary Format

```text
Principal: user@example.com (configuration: sandbox)
Project: example-sandbox (number: 123456789012)

Found:
- europe-west1-b Compute Engine: vm-a, disk-a
- europe-west1 Cloud SQL: sql-a
- global Cloud Storage: bucket-a (versioning enabled)

Coverage gaps:
- Cloud Asset Inventory: permission denied; direct checks used for listed services
- Cloud Run in other regions: not yet checked

Deletion blockers:
- sql-a has deletion protection enabled
- bucket-a has retained object versions

Choose `all` or list exact resources/services/locations to remove from example-sandbox.
```
