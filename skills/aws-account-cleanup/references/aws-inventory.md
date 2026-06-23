# AWS Inventory Checklist

Use this reference after the required access confirmation. Keep commands read-only during dry run.

## Account

```bash
aws sts get-caller-identity
aws iam list-account-aliases
```

## Regions

```bash
aws ec2 describe-regions --all-regions --query 'Regions[?OptInStatus==`opt-in-not-required` || OptInStatus==`opted-in`].RegionName' --output text
```

Run regional checks with `--region "$region"`.

## Regional Checks

```bash
aws ec2 describe-instances --region "$region"
aws ec2 describe-volumes --region "$region"
aws ec2 describe-snapshots --owner-ids self --region "$region"
aws ec2 describe-addresses --region "$region"
aws ec2 describe-nat-gateways --region "$region"
aws ec2 describe-vpcs --region "$region"
aws ec2 describe-subnets --region "$region"
aws ec2 describe-internet-gateways --region "$region"
aws ec2 describe-vpc-endpoints --region "$region"
aws elbv2 describe-load-balancers --region "$region"
aws elbv2 describe-target-groups --region "$region"
aws rds describe-db-instances --region "$region"
aws rds describe-db-clusters --region "$region"
aws rds describe-db-snapshots --region "$region"
aws ecs list-clusters --region "$region"
aws eks list-clusters --region "$region"
aws lambda list-functions --region "$region"
aws events list-rules --region "$region"
aws logs describe-log-groups --region "$region"
aws secretsmanager list-secrets --region "$region"
aws ssm describe-parameters --region "$region"
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE UPDATE_ROLLBACK_COMPLETE IMPORT_COMPLETE ROLLBACK_COMPLETE --region "$region"
aws acm list-certificates --region "$region"
aws wafv2 list-web-acls --scope REGIONAL --region "$region"
```

## Global Checks

```bash
aws s3api list-buckets
aws cloudfront list-distributions
aws route53 list-hosted-zones
aws iam list-users
aws iam list-roles
aws iam list-policies --scope Local
aws iam list-groups
aws iam list-instance-profiles
```

For S3, resolve each bucket region before planning deletion:

```bash
aws s3api get-bucket-location --bucket "$bucket"
aws s3api get-bucket-versioning --bucket "$bucket"
aws s3api get-bucket-encryption --bucket "$bucket"
aws s3api get-public-access-block --bucket "$bucket"
```

## Summary Format

Report findings like this:

```text
Account: 123456789012 (profile: sandbox)

Found:
- eu-west-1 EC2: 2 instances, 3 EBS volumes, 1 elastic IP
- eu-west-1 RDS: 1 DB instance, 2 snapshots
- global S3: 4 buckets, 2 versioned
- global IAM: 3 users, 8 roles, 5 customer-managed policies

Deletion blockers:
- bucket-a is versioned and must be emptied by version/delete-marker
- i-abc has termination protection enabled
- hosted zone Z123 has non-default records

Choose `all` or list exact resources/services/regions to remove.
```
