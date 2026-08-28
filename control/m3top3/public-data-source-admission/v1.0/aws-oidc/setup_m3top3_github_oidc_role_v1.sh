#!/usr/bin/env bash
set -euo pipefail
export AWS_PAGER=''
command -v aws >/dev/null
command -v jq >/dev/null

AWS_REGION='ap-northeast-2'
S3_BUCKET='semi-data-plane-aofspds-20260815'
ROLE_NAME='M3Top3GitHubOIDCRawWriter'
INLINE_POLICY_NAME='M3Top3PublicDataRawWriter'
GITHUB_REPOSITORY='AofSpds/asset-agent-asa'
GITHUB_ENVIRONMENT='m3top3-source-admission'
OIDC_URL='https://token.actions.githubusercontent.com'
OIDC_AUDIENCE='sts.amazonaws.com'

AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
test -n "$AWS_ACCOUNT_ID"
test "$AWS_ACCOUNT_ID" != "None"

aws s3api head-bucket --bucket "$S3_BUCKET"
BUCKET_REGION="$(aws s3api get-bucket-location --bucket "$S3_BUCKET" --query LocationConstraint --output text)"
test "$BUCKET_REGION" = "$AWS_REGION"
VERSIONING="$(aws s3api get-bucket-versioning --bucket "$S3_BUCKET" --query Status --output text)"
test "$VERSIONING" = "Enabled"

OIDC_PROVIDER_ARN="arn:aws:iam::$AWS_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_PROVIDER_ARN" >/dev/null 2>&1; then
  PROVIDER_JSON="$(aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_PROVIDER_ARN")"
  if ! jq -e --arg audience "$OIDC_AUDIENCE" '.ClientIDList | index($audience) != null' <<< "$PROVIDER_JSON" >/dev/null; then
    aws iam add-client-id-to-open-id-connect-provider \
      --open-id-connect-provider-arn "$OIDC_PROVIDER_ARN" \
      --client-id "$OIDC_AUDIENCE"
  fi
else
  aws iam create-open-id-connect-provider \
    --url "$OIDC_URL" \
    --client-id-list "$OIDC_AUDIENCE" >/dev/null
fi

TASK_TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TASK_TMP_DIR"' EXIT

jq -n \
  --arg provider "$OIDC_PROVIDER_ARN" \
  --arg sub "repo:$GITHUB_REPOSITORY:environment:$GITHUB_ENVIRONMENT" \
  '{
    Version:"2012-10-17",
    Statement:[{
      Sid:"GitHubActionsOIDCEnvironmentOnly",
      Effect:"Allow",
      Principal:{Federated:$provider},
      Action:"sts:AssumeRoleWithWebIdentity",
      Condition:{StringEquals:{
        "token.actions.githubusercontent.com:aud":"sts.amazonaws.com",
        "token.actions.githubusercontent.com:sub":$sub
      }}
    }]
  }' > "$TASK_TMP_DIR/trust.json"

jq -n \
  --arg bucket "$S3_BUCKET" \
  '{
    Version:"2012-10-17",
    Statement:[
      {
        Sid:"BucketMetadataReadOnly",
        Effect:"Allow",
        Action:["s3:GetBucketLocation","s3:GetBucketVersioning"],
        Resource:("arn:aws:s3:::"+$bucket)
      },
      {
        Sid:"RestrictedSourcePrefixList",
        Effect:"Allow",
        Action:"s3:ListBucket",
        Resource:("arn:aws:s3:::"+$bucket),
        Condition:{StringLike:{"s3:prefix":[
          "raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/*",
          "raw/public-data-api/M3TOP3-KSD-CORP-DATA-GO-KR-v1/*"
        ]}}
      },
      {
        Sid:"SourcePrefixWriteAndReadNoDelete",
        Effect:"Allow",
        Action:["s3:PutObject","s3:GetObject","s3:GetObjectVersion"],
        Resource:[
          ("arn:aws:s3:::"+$bucket+"/raw/public-data-api/M3TOP3-FINANCE-STOCK-RIGHTS-v1/*"),
          ("arn:aws:s3:::"+$bucket+"/raw/public-data-api/M3TOP3-KSD-CORP-DATA-GO-KR-v1/*")
        ]
      }
    ]
  }' > "$TASK_TMP_DIR/permissions.json"

if aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
  ATTACHED_POLICIES="$(aws iam list-attached-role-policies --role-name "$ROLE_NAME")"
  INLINE_POLICIES="$(aws iam list-role-policies --role-name "$ROLE_NAME")"
  if ! jq -e '.AttachedPolicies | length == 0' <<< "$ATTACHED_POLICIES" >/dev/null; then
    echo "Existing role has unexpected attached policies; stop for inspection." >&2
    exit 3
  fi
  if ! jq -e --arg expected "$INLINE_POLICY_NAME" 'all(.PolicyNames[]?; . == $expected)' <<< "$INLINE_POLICIES" >/dev/null; then
    echo "Existing role has an unexpected inline policy; stop for inspection." >&2
    exit 3
  fi
  aws iam update-assume-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-document "file://$TASK_TMP_DIR/trust.json"
else
  aws iam create-role \
    --role-name "$ROLE_NAME" \
    --description 'GitHub OIDC writer for M3Top3 public-data raw prefixes only' \
    --assume-role-policy-document "file://$TASK_TMP_DIR/trust.json" \
    --max-session-duration 3600 >/dev/null
fi

aws iam put-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-name "$INLINE_POLICY_NAME" \
  --policy-document "file://$TASK_TMP_DIR/permissions.json"

FINAL_ATTACHED_POLICIES="$(aws iam list-attached-role-policies --role-name "$ROLE_NAME")"
FINAL_INLINE_POLICIES="$(aws iam list-role-policies --role-name "$ROLE_NAME")"
jq -e '.AttachedPolicies | length == 0' <<< "$FINAL_ATTACHED_POLICIES" >/dev/null
jq -e --arg expected "$INLINE_POLICY_NAME" '.PolicyNames == [$expected]' <<< "$FINAL_INLINE_POLICIES" >/dev/null

ROLE_ARN="$(aws iam get-role --role-name "$ROLE_NAME" --query Role.Arn --output text)"
test -n "$ROLE_ARN"

printf 'ROLE_ARN=%s\n' "$ROLE_ARN"
printf 'GITHUB_ENVIRONMENT=%s\n' "$GITHUB_ENVIRONMENT"
printf 'GITHUB_VARIABLE=%s\n' 'M3TOP3_AWS_ROLE_ARN'
