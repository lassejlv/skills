#!/usr/bin/env bash
set -u

usage() {
  cat <<'EOF'
Usage: aws-context.sh [--profile PROFILE] [--region REGION] [--all-profiles] [--skip-sts]

Print read-only AWS CLI context: CLI version, relevant environment status,
configured profiles, resolved region, and STS caller identity.

No AWS secret values are printed. No resources are created, updated, or deleted.
EOF
}

profile=""
region=""
all_profiles=0
skip_sts=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      [[ $# -ge 2 ]] || { echo "missing value for --profile" >&2; exit 2; }
      profile="$2"
      shift 2
      ;;
    --region)
      [[ $# -ge 2 ]] || { echo "missing value for --region" >&2; exit 2; }
      region="$2"
      shift 2
      ;;
    --all-profiles)
      all_profiles=1
      shift
      ;;
    --skip-sts)
      skip_sts=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

hide_or_show_env() {
  local name="$1"
  local value="${!name-}"

  if [[ -z "$value" ]]; then
    printf '%s=unset\n' "$name"
    return
  fi

  case "$name" in
    AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN)
      printf '%s=set (hidden)\n' "$name"
      ;;
    *)
      printf '%s=%s\n' "$name" "$value"
      ;;
  esac
}

aws_base_args_for_profile() {
  local selected_profile="$1"
  if [[ -n "$selected_profile" ]]; then
    printf '%s\0%s\0' "--profile" "$selected_profile"
  fi
}

resolve_region() {
  local selected_profile="$1"

  if [[ -n "$region" ]]; then
    printf '%s\n' "$region"
    return
  fi
  if [[ -n "${AWS_REGION-}" ]]; then
    printf '%s\n' "$AWS_REGION"
    return
  fi
  if [[ -n "${AWS_DEFAULT_REGION-}" ]]; then
    printf '%s\n' "$AWS_DEFAULT_REGION"
    return
  fi
  if [[ -n "$selected_profile" ]]; then
    aws --profile "$selected_profile" configure get region 2>/dev/null || true
    return
  fi
  aws configure get region 2>/dev/null || true
}

run_sts() {
  local selected_profile="$1"
  local selected_region="$2"
  local args=()

  if [[ -n "$selected_profile" ]]; then
    args+=(--profile "$selected_profile")
  fi
  if [[ -n "$selected_region" ]]; then
    args+=(--region "$selected_region")
  fi

  printf '\n== STS caller identity'
  if [[ -n "$selected_profile" ]]; then
    printf ' for profile %s' "$selected_profile"
  else
    printf ' for default credential chain'
  fi
  printf ' ==\n'

  if [[ "$skip_sts" -eq 1 ]]; then
    echo "skipped (--skip-sts)"
    return
  fi

  local output
  if output="$(aws "${args[@]}" sts get-caller-identity --output json 2>&1)"; then
    printf '%s\n' "$output"
  else
    echo "failed:"
    printf '%s\n' "$output" | sed 's/^/  /'
  fi
}

if ! command -v aws >/dev/null 2>&1; then
  echo "aws CLI not found on PATH" >&2
  exit 1
fi

if [[ -z "$profile" ]]; then
  profile="${AWS_PROFILE-${AWS_DEFAULT_PROFILE-}}"
fi

resolved_region="$(resolve_region "$profile")"

echo "== AWS CLI =="
aws --version

echo
echo "== Relevant environment =="
for var_name in \
  AWS_PROFILE \
  AWS_DEFAULT_PROFILE \
  AWS_REGION \
  AWS_DEFAULT_REGION \
  AWS_ACCESS_KEY_ID \
  AWS_SECRET_ACCESS_KEY \
  AWS_SESSION_TOKEN \
  AWS_ROLE_ARN \
  AWS_WEB_IDENTITY_TOKEN_FILE \
  AWS_CONFIG_FILE \
  AWS_SHARED_CREDENTIALS_FILE
do
  hide_or_show_env "$var_name"
done

echo
echo "== Configured profiles =="
if ! aws configure list-profiles 2>/dev/null; then
  echo "(could not list profiles)"
fi

echo
echo "== Selected context =="
if [[ -n "$profile" ]]; then
  echo "profile=$profile"
else
  echo "profile=(default credential chain)"
fi
if [[ -n "$resolved_region" ]]; then
  echo "region=$resolved_region"
else
  echo "region=(not configured)"
fi

if [[ "$all_profiles" -eq 1 ]]; then
  while IFS= read -r listed_profile; do
    [[ -n "$listed_profile" ]] || continue
    listed_region="$(resolve_region "$listed_profile")"
    run_sts "$listed_profile" "$listed_region"
  done < <(aws configure list-profiles 2>/dev/null || true)
else
  run_sts "$profile" "$resolved_region"
fi
