# M3Top3 GitHub Environment and AWS OIDC setup v1.0

Complete the protected GitHub Environment check before creating the AWS role.

## 1. GitHub Environment capability and protection

1. Repository: `AofSpds/asset-agent-asa`
2. Settings → Environments → New environment
3. Exact name: `m3top3-source-admission`
4. Deployment branches and tags: choose **Selected branches and tags**
5. Add the exact branch: `aaa-pmo-public-data-g2-g3-source-admission-v1-20260828`
6. Do not choose **Protected branches only**; this branch is not branch-protected.
7. If **Required reviewers** is available, add `AofSpds`, leave **Prevent self-review** off for the sole-owner approval path, and disable administrator bypass if the UI offers that control.
8. If Required reviewers is unavailable for this private repository, do not continue automatically. The owner must first verify that no other user, team, deploy key, or installed GitHub App has write/admin authority. If that single-owner condition cannot be proven, use a manual AWS CloudShell custody upload instead of Actions OIDC.

## 2. AWS CloudShell

Run the pinned repository script only after step 1 is safe:

`control/m3top3/public-data-source-admission/v1.0/aws-oidc/setup_m3top3_github_oidc_role_v1.sh`

The script:

- verifies the account can access `semi-data-plane-aofspds-20260815` in `ap-northeast-2` and that versioning is enabled;
- creates or reuses the GitHub OIDC provider and ensures audience `sts.amazonaws.com` is present;
- refuses an existing role that has any unexpected attached or inline policy;
- creates or updates `M3Top3GitHubOIDCRawWriter`;
- prints `ROLE_ARN=...`.

## 3. Bind the non-secret role ARN

In Environment `m3top3-source-admission`, create Environment variable:

- Name: `M3TOP3_AWS_ROLE_ARN`
- Value: the printed `ROLE_ARN`

Do not create `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, or an AWS session-token secret.

## 4. First execution

The workflow is not on the default branch, so GitHub UI `workflow_dispatch` is not the first-run path. After the owner binding is confirmed, PMO changes only this latch file:

`control/m3top3/public-data-source-admission/v1.0/M3TOP3_PUBLIC_DATA_API_S3_CUSTODY_PUSH_LATCH_v1.0.json`

The task-branch push runs only with all of these exact gates:

- actor is repository owner;
- branch is `aaa-pmo-public-data-g2-g3-source-admission-v1-20260828`;
- changed path is the latch file above;
- commit message is `MATERIALIZE_ARTIFACT_9670226482_ONCE`;
- environment protection admits the deployment.

If a required reviewer is configured, approve the waiting deployment. The workflow reuses artifact `9670226482`, makes zero new provider API calls, uploads one immutable 143-byte entity, and verifies the remote SHA-256. The source artifact expires at `2026-09-04T00:50:26Z`.
