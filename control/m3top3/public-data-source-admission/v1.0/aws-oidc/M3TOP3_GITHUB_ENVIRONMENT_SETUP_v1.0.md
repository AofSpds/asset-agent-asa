# M3Top3 GitHub Environment setup v1.0

Create one protected GitHub Environment after the AWS setup script prints the role ARN.

1. Repository: `AofSpds/asset-agent-asa`
2. Settings → Environments → New environment
3. Exact name: `m3top3-source-admission`
4. Add required reviewer: repository owner `AofSpds`
5. Deployment branches/tags: selected branch only
6. Exact allowed branch: `aaa-pmo-public-data-g2-g3-source-admission-v1-20260828`
7. Environment variable name: `M3TOP3_AWS_ROLE_ARN`
8. Environment variable value: the `ROLE_ARN` printed by `setup_m3top3_github_oidc_role_v1.sh`
9. Do not create `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, or an AWS session-token secret.
10. If required-reviewer or selected-branch protection is unavailable, stop. Do not dispatch the custody workflow with an unprotected environment.

Prepared workflow:
`.github/workflows/m3top3-s3-raw-custody-single-canary-v1.yml`

First dispatch confirmation:
`MATERIALIZE_ARTIFACT_9670226482_ONCE`
