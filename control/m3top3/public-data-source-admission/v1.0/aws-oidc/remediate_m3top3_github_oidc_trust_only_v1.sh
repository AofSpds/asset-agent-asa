#!/usr/bin/env bash
set -euo pipefail
export AWS_PAGER=''

readonly EXPECTED_ACCOUNT_ID='956315449338'
readonly EXPECTED_ROLE_NAME='M3Top3GitHubOIDCRawWriter'
readonly EXPECTED_ROLE_ARN='arn:aws:iam::956315449338:role/M3Top3GitHubOIDCRawWriter'
readonly EXPECTED_PROVIDER_ARN='arn:aws:iam::956315449338:oidc-provider/token.actions.githubusercontent.com'
readonly EXPECTED_PROVIDER_URL='token.actions.githubusercontent.com'
readonly EXPECTED_AUDIENCE='sts.amazonaws.com'
readonly EXPECTED_SUBJECT='repo:AofSpds@87963280/asset-agent-asa@1334403184:environment:m3top3-source-admission'
readonly PREVIOUS_SUBJECT='repo:AofSpds/asset-agent-asa:environment:m3top3-source-admission'
readonly TEMPLATE_ACCOUNT_PLACEHOLDER='<AWS_ACCOUNT_ID>'
readonly TEMPLATE_NAME='M3TOP3_AWS_GITHUB_OIDC_TRUST_POLICY_TEMPLATE_v1.0.json'

usage() {
  printf '%s\n' \
    "Usage: bash $(basename -- "$0") --apply" \
    'This command changes only the named role trust policy.' >&2
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

if [[ $# -ne 1 || "$1" != '--apply' ]]; then
  usage
  exit 64
fi

command -v aws >/dev/null 2>&1 || die 'aws CLI is required'
command -v jq >/dev/null 2>&1 || die 'jq is required'
command -v sha256sum >/dev/null 2>&1 || die 'sha256sum is required'
command -v cmp >/dev/null 2>&1 || die 'cmp is required'

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly TEMPLATE_PATH="$SCRIPT_DIR/$TEMPLATE_NAME"
[[ -f "$TEMPLATE_PATH" ]] || die "missing trust template: $TEMPLATE_PATH"

readonly TASK_TMP_DIR="$(mktemp -d)"
[[ -n "$TASK_TMP_DIR" && -d "$TASK_TMP_DIR" ]] || die 'mktemp failed'
cleanup() {
  rm -rf -- "$TASK_TMP_DIR"
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

write_expected_trust() {
  local provider_arn="$1"
  local subject="$2"
  local output_path="$3"
  jq -S -n \
    --arg provider "$provider_arn" \
    --arg audience "$EXPECTED_AUDIENCE" \
    --arg subject "$subject" \
    '{
      Version: "2012-10-17",
      Statement: [
        {
          Sid: "GitHubActionsOIDCEnvironmentOnly",
          Effect: "Allow",
          Principal: {Federated: $provider},
          Action: "sts:AssumeRoleWithWebIdentity",
          Condition: {
            StringEquals: {
              "token.actions.githubusercontent.com:aud": $audience,
              "token.actions.githubusercontent.com:sub": $subject
            }
          }
        }
      ]
    }' > "$output_path"
}

canonical_role_trust() {
  local role_json_path="$1"
  local output_path="$2"
  jq -S '.Role.AssumeRolePolicyDocument' "$role_json_path" > "$output_path"
  jq -e 'type == "object"' "$output_path" >/dev/null
}

snapshot_managed_policy() {
  local policy_arn="$1"
  local association_json="$2"
  local output_path="$3"
  local policy_json version_id version_json

  policy_json="$(aws iam get-policy --policy-arn "$policy_arn" --output json)"
  version_id="$(jq -er '.Policy.DefaultVersionId | select(type == "string" and length > 0)' <<< "$policy_json")"
  version_json="$(aws iam get-policy-version \
    --policy-arn "$policy_arn" \
    --version-id "$version_id" \
    --output json)"
  jq -S -n \
    --argjson association "$association_json" \
    --arg version_id "$version_id" \
    --argjson version "$version_json" \
    '{
      association: {
        PolicyName: $association.PolicyName,
        PolicyArn: $association.PolicyArn
      },
      default_version: {
        VersionId: $version_id,
        Document: $version.PolicyVersion.Document
      }
    }' > "$output_path"
}

snapshot_non_trust_state() {
  local output_path="$1"
  local snapshot_dir="$2"
  local role_json attached_json inline_names_json
  local boundary_arn boundary_association boundary_snapshot
  local association policy_arn policy_name policy_json
  local attached_item_path
  local attached_index=0
  local -a inline_names=()

  mkdir -p -- "$snapshot_dir/attached" "$snapshot_dir/inline"
  : > "$snapshot_dir/attached.jsonl"
  : > "$snapshot_dir/inline.jsonl"
  role_json="$(aws iam get-role --role-name "$EXPECTED_ROLE_NAME" --output json)"
  jq -e \
    --arg name "$EXPECTED_ROLE_NAME" \
    --arg arn "$EXPECTED_ROLE_ARN" \
    '.Role.RoleName == $name and .Role.Arn == $arn' \
    <<< "$role_json" >/dev/null || die 'role identity changed during snapshot'

  attached_json="$(aws iam list-attached-role-policies \
    --role-name "$EXPECTED_ROLE_NAME" \
    --output json)"
  jq -e '.AttachedPolicies | type == "array"' <<< "$attached_json" >/dev/null
  while IFS= read -r association; do
    [[ -n "$association" ]] || continue
    policy_arn="$(jq -er '.PolicyArn' <<< "$association")"
    policy_name="$(jq -er '.PolicyName' <<< "$association")"
    attached_item_path="$snapshot_dir/attached/$attached_index.json"
    snapshot_managed_policy \
      "$policy_arn" \
      "$association" \
      "$attached_item_path"
    jq -c . "$attached_item_path" >> "$snapshot_dir/attached.jsonl"
    attached_index=$((attached_index + 1))
  done < <(jq -c '.AttachedPolicies | sort_by(.PolicyArn)[]' <<< "$attached_json")
  jq -S -s 'sort_by(.association.PolicyArn)' "$snapshot_dir/attached.jsonl" \
    > "$snapshot_dir/attached.json"

  inline_names_json="$(aws iam list-role-policies \
    --role-name "$EXPECTED_ROLE_NAME" \
    --output json)"
  jq -e '.PolicyNames | type == "array"' <<< "$inline_names_json" >/dev/null
  mapfile -t inline_names < <(jq -r '.PolicyNames | sort[]' <<< "$inline_names_json")
  for policy_name in "${inline_names[@]}"; do
    policy_json="$(aws iam get-role-policy \
      --role-name "$EXPECTED_ROLE_NAME" \
      --policy-name "$policy_name" \
      --output json)"
    jq -S \
      '{PolicyName: .PolicyName, PolicyDocument: .PolicyDocument}' \
      <<< "$policy_json" > "$snapshot_dir/inline/$policy_name.json"
    jq -c . "$snapshot_dir/inline/$policy_name.json" >> "$snapshot_dir/inline.jsonl"
  done
  jq -S -s 'sort_by(.PolicyName)' "$snapshot_dir/inline.jsonl" \
    > "$snapshot_dir/inline.json"

  boundary_arn="$(jq -r '.Role.PermissionsBoundary.PermissionsBoundaryArn // empty' <<< "$role_json")"
  if [[ -n "$boundary_arn" ]]; then
    boundary_association="$(jq -n \
      --arg arn "$boundary_arn" \
      --arg name "${boundary_arn##*/}" \
      '{PolicyArn: $arn, PolicyName: $name}')"
    boundary_snapshot="$snapshot_dir/boundary.json"
    snapshot_managed_policy "$boundary_arn" "$boundary_association" "$boundary_snapshot"
  else
    boundary_snapshot="$snapshot_dir/boundary.json"
    printf '%s\n' 'null' > "$boundary_snapshot"
  fi

  jq -S -n \
    --argjson role "$role_json" \
    --slurpfile attached "$snapshot_dir/attached.json" \
    --slurpfile inline "$snapshot_dir/inline.json" \
    --slurpfile boundary "$boundary_snapshot" \
    '{
      role_identity: {
        RoleName: $role.Role.RoleName,
        RoleId: $role.Role.RoleId,
        Arn: $role.Role.Arn
      },
      attached_managed_policies: $attached[0],
      inline_policies: $inline[0],
      permissions_boundary: (
        if $boundary[0] == null then
          null
        else
          $boundary[0] + {
            boundary_type: $role.Role.PermissionsBoundary.PermissionsBoundaryType
          }
        end
      ),
      max_session_duration: $role.Role.MaxSessionDuration
    }' > "$output_path"
}

write_expected_trust \
  "arn:aws:iam::$TEMPLATE_ACCOUNT_PLACEHOLDER:oidc-provider/token.actions.githubusercontent.com" \
  "$EXPECTED_SUBJECT" \
  "$TASK_TMP_DIR/expected-template.json"
jq -S . "$TEMPLATE_PATH" > "$TASK_TMP_DIR/canonical-template.json"
cmp -s "$TASK_TMP_DIR/expected-template.json" "$TASK_TMP_DIR/canonical-template.json" \
  || die 'checked-in trust template is not the exact approved StringEquals template'

write_expected_trust "$EXPECTED_PROVIDER_ARN" "$EXPECTED_SUBJECT" "$TASK_TMP_DIR/target-trust.json"
write_expected_trust "$EXPECTED_PROVIDER_ARN" "$PREVIOUS_SUBJECT" "$TASK_TMP_DIR/previous-trust.json"

caller_json="$(aws sts get-caller-identity --output json)"
jq -e --arg account "$EXPECTED_ACCOUNT_ID" '.Account == $account' \
  <<< "$caller_json" >/dev/null || die 'AWS caller is not in the exact authorized account'

provider_json="$(aws iam get-open-id-connect-provider \
  --open-id-connect-provider-arn "$EXPECTED_PROVIDER_ARN" \
  --output json)"
jq -e \
  --arg url "$EXPECTED_PROVIDER_URL" \
  --arg audience "$EXPECTED_AUDIENCE" \
  '.Url == $url and (.ClientIDList | index($audience) != null)' \
  <<< "$provider_json" >/dev/null \
  || die 'exact GitHub OIDC provider or required audience is absent'

aws iam get-role --role-name "$EXPECTED_ROLE_NAME" --output json \
  > "$TASK_TMP_DIR/role-before.json"
jq -e \
  --arg name "$EXPECTED_ROLE_NAME" \
  --arg arn "$EXPECTED_ROLE_ARN" \
  '.Role.RoleName == $name and .Role.Arn == $arn' \
  "$TASK_TMP_DIR/role-before.json" >/dev/null \
  || die 'exact authorized role was not found'
canonical_role_trust "$TASK_TMP_DIR/role-before.json" "$TASK_TMP_DIR/trust-before.json"

if cmp -s "$TASK_TMP_DIR/trust-before.json" "$TASK_TMP_DIR/target-trust.json"; then
  trust_state='ALREADY_TARGET'
elif cmp -s "$TASK_TMP_DIR/trust-before.json" "$TASK_TMP_DIR/previous-trust.json"; then
  trust_state='EXACT_PREVIOUS_TEMPLATE'
else
  die 'current trust is neither the exact previous template nor the exact target; no write performed'
fi

snapshot_non_trust_state \
  "$TASK_TMP_DIR/non-trust-before.json" \
  "$TASK_TMP_DIR/snapshot-before"
before_fingerprint="$(sha256sum "$TASK_TMP_DIR/non-trust-before.json" | awk '{print $1}')"

# Re-read both trust and non-trust state immediately before the only mutating API call.
aws iam get-role --role-name "$EXPECTED_ROLE_NAME" --output json \
  > "$TASK_TMP_DIR/role-cas.json"
canonical_role_trust "$TASK_TMP_DIR/role-cas.json" "$TASK_TMP_DIR/trust-cas.json"
cmp -s "$TASK_TMP_DIR/trust-before.json" "$TASK_TMP_DIR/trust-cas.json" \
  || die 'trust changed during preflight; no write performed'
snapshot_non_trust_state \
  "$TASK_TMP_DIR/non-trust-cas.json" \
  "$TASK_TMP_DIR/snapshot-cas"
cmp -s "$TASK_TMP_DIR/non-trust-before.json" "$TASK_TMP_DIR/non-trust-cas.json" \
  || die 'permissions, boundary, or max-session state changed during preflight; no write performed'

if [[ "$trust_state" == 'EXACT_PREVIOUS_TEMPLATE' ]]; then
  aws iam update-assume-role-policy \
    --role-name "$EXPECTED_ROLE_NAME" \
    --policy-document "file://$TASK_TMP_DIR/target-trust.json"
  mutation_performed='true'
else
  mutation_performed='false'
fi

trust_proven='false'
for attempt in 1 2 3 4 5; do
  aws iam get-role --role-name "$EXPECTED_ROLE_NAME" --output json \
    > "$TASK_TMP_DIR/role-after.json"
  canonical_role_trust "$TASK_TMP_DIR/role-after.json" "$TASK_TMP_DIR/trust-after.json"
  if cmp -s "$TASK_TMP_DIR/trust-after.json" "$TASK_TMP_DIR/target-trust.json"; then
    trust_proven='true'
    break
  fi
  if [[ "$attempt" -lt 5 ]]; then
    sleep 2
  fi
done
[[ "$trust_proven" == 'true' ]] \
  || die 'target trust was not observable after the bounded verification reads'

snapshot_non_trust_state \
  "$TASK_TMP_DIR/non-trust-after.json" \
  "$TASK_TMP_DIR/snapshot-after"
after_fingerprint="$(sha256sum "$TASK_TMP_DIR/non-trust-after.json" | awk '{print $1}')"
cmp -s "$TASK_TMP_DIR/non-trust-before.json" "$TASK_TMP_DIR/non-trust-after.json" \
  || die 'non-trust role state changed; inspect immediately'

target_trust_fingerprint="$(sha256sum "$TASK_TMP_DIR/target-trust.json" | awk '{print $1}')"
printf 'RESULT=TRUST_ONLY_REMEDIATION_PROVEN\n'
printf 'MUTATION_PERFORMED=%s\n' "$mutation_performed"
printf 'ROLE_ARN=%s\n' "$EXPECTED_ROLE_ARN"
printf 'OIDC_PROVIDER_ARN=%s\n' "$EXPECTED_PROVIDER_ARN"
printf 'OIDC_AUDIENCE=%s\n' "$EXPECTED_AUDIENCE"
printf 'OIDC_SUBJECT=%s\n' "$EXPECTED_SUBJECT"
printf 'TARGET_TRUST_SHA256=%s\n' "$target_trust_fingerprint"
printf 'NON_TRUST_STATE_BEFORE_SHA256=%s\n' "$before_fingerprint"
printf 'NON_TRUST_STATE_AFTER_SHA256=%s\n' "$after_fingerprint"
printf 'ATTACHED_INLINE_BOUNDARY_MAX_SESSION_UNCHANGED=true\n'
