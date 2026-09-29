# workflows

Reusable GitHub Actions workflows for [Abijith Suresh](https://github.com/abijith-suresh)'s repositories, and a reference project for safe workflow design.

Application-specific triggers, matrices, smoke tests, deployments, publishing, and exceptional package layouts stay in each consuming repository. The shared workflows provide small, explicit contracts so those projects can use the same quality and release setup.

## Workflow contracts

| Workflow | Caller contract |
| --- | --- |
| [`bun-quality.yml`](.github/workflows/bun-quality.yml) | Root `mise.toml` with one exact Bun version, `bun.lock`, `package.json`, and `verify` script. Runs `bun install --frozen-lockfile` and `bun run verify`. |
| [`npm-quality.yml`](.github/workflows/npm-quality.yml) | Root `mise.toml` with one exact Node and npm version, `package-lock.json`, `package.json`, and `verify` script. Runs `npm ci` and `npm run verify`. |
| [`conventional-commit-title.yml`](.github/workflows/conventional-commit-title.yml) | PR title uses a supported Conventional Commit type, has at most 72 characters, and has no trailing period. Dependabot is exempt. |
| [`dependency-review.yml`](.github/workflows/dependency-review.yml) | Public repository, or a private repository with the required GitHub security licensing. Default severity threshold is `high`. |
| [`dependabot-auto-merge.yml`](.github/workflows/dependabot-auto-merge.yml) | Caller uses `pull_request`, maps a repo-scoped fine-grained token from Dependabot secrets, and selects one of two documented major-update policies. |
| [`release-please.yml`](.github/workflows/release-please.yml) | Root Release Please config and manifest, both no-`v` options set to `false`, and a `RELEASE_PLEASE_TOKEN` secret. Caller owns release triggers and branch filters. |
| [`vercel-preview-cleanup.yml`](.github/workflows/vercel-preview-cleanup.yml) | Closed pull request event, Vercel project and scope, and a named project-scoped token. Removes matching preview deployments across all result pages. |
| [`policy.yml`](.github/workflows/policy.yml) | Local deterministic checks for this repository: actionlint, whitespace, release metadata, and PR title. |

The workflow files are the source of truth. Quality workflows intentionally accept no commands or directory overrides. A project with a different layout can keep its quality workflow local or add a root compatibility wrapper.

## Calling a reusable workflow

Pin every shared workflow to the full commit SHA of a published release. Keep the release version in a comment for humans. The examples below use `<WORKFLOWS_SHA>` as a placeholder; replace it with the 40-character SHA before use. A version tag in the comment does not replace the SHA pin.

### Quality checks

Choose the workflow for the repository's package manager. Keep the root `verify` script as the one shared entry point; it can call package-specific checks owned by that project.

```yaml
name: Quality

on:
  pull_request:

permissions:
  contents: read

jobs:
  bun-quality:
    uses: abijith-suresh/workflows/.github/workflows/bun-quality.yml@<WORKFLOWS_SHA> # vX.Y.Z
    permissions:
      contents: read

  npm-quality:
    uses: abijith-suresh/workflows/.github/workflows/npm-quality.yml@<WORKFLOWS_SHA> # vX.Y.Z
    permissions:
      contents: read
```

Only include the job for the package manager used by that repository. Both workflows read runtime versions from the caller's root `mise.toml`; they do not use a runtime file from this repository. Declare each runtime exactly once under `[tools]` using `major.minor.patch` values:

```toml
# Bun caller
[tools]
bun = "1.4.1"
```

```toml
# npm caller
[tools]
node = "24.20.0"
npm = "11.16.0"
```

The shared jobs do not read `.bun-version`, `.node-version`, `packageManager`, or caller environment variables for runtime selection. Reconcile duplicate runtime declarations during migration.

### Title and dependency checks

```yaml
jobs:
  pr-title:
    uses: abijith-suresh/workflows/.github/workflows/conventional-commit-title.yml@<WORKFLOWS_SHA> # vX.Y.Z
    permissions:
      pull-requests: read

  dependency-review:
    uses: abijith-suresh/workflows/.github/workflows/dependency-review.yml@<WORKFLOWS_SHA> # vX.Y.Z
    with:
      fail-on-severity: high # low | moderate | high | critical
    permissions:
      contents: read
```

Dependency Review is supported on public repositories and on private repositories with the required GitHub security licensing. Each repository can keep a local dependency-review configuration when it needs project-specific license or scope rules.

### Dependabot auto-merge

Call this only for `pull_request` events. Dependabot-triggered `GITHUB_TOKEN`s are read-only, so pass a fine-grained personal access token stored as a **Dependabot secret**. The token must be limited to the target repository and grant `Contents: write` and `Pull requests: write`. With `compatible-majors`, the pinned metadata action uses this token to look up compatibility scores. With `patch-minor`, it uses the read-only `GITHUB_TOKEN`. The merge steps use the fine-grained token to request auto-merge. GitHub Actions dependency updates always require manual review.

```yaml
name: Dependabot auto-merge

on:
  pull_request:
    types:
      - opened
      - reopened
      - synchronize

permissions: {}

jobs:
  dependabot-auto-merge:
    if: >-
      github.actor == 'dependabot[bot]' &&
      github.event.pull_request.user.login == 'dependabot[bot]'
    uses: abijith-suresh/workflows/.github/workflows/dependabot-auto-merge.yml@<WORKFLOWS_SHA> # vX.Y.Z
    with:
      major-update-policy: compatible-majors # or patch-minor
    permissions:
      contents: read
      pull-requests: read
    secrets:
      DEPENDABOT_AUTOMERGE_TOKEN: ${{ secrets.DEPENDABOT_TOKEN }}
```

Replace `DEPENDABOT_TOKEN` with the name of the token already stored under the repository's Dependabot secrets. The called workflow checks that both the event actor and PR author are `dependabot[bot]`, fetches update metadata, and requests squash auto-merge only for eligible updates. It does not check out or execute pull-request code. `compatible-majors` allows major updates to direct development dependencies and direct production dependencies with a known compatibility score of at least 90. `patch-minor` only enables patch and minor updates. Neither policy auto-merges GitHub Actions updates. Auto-merge must be allowed in repository settings; branch protection and required checks still gate the merge.

### Releases and release branches

The reusable workflow only runs for branch `push` and `workflow_dispatch` calls. Each caller owns the events and branch filters. For multiple release branches, call it for those branches and pass the triggering branch as `target-branch`:

```yaml
name: Release Please

on:
  push:
    branches:
      - main
      - 1.x

permissions: {}

jobs:
  release-please:
    uses: abijith-suresh/workflows/.github/workflows/release-please.yml@<WORKFLOWS_SHA> # vX.Y.Z
    with:
      target-branch: ${{ github.ref_name }}
    permissions:
      contents: write
      issues: write
      pull-requests: write
    secrets:
      RELEASE_PLEASE_TOKEN: ${{ secrets.RELEASE_PLEASE_TOKEN }}
```

`target-branch` is optional and defaults to the caller's branch. Callers using the ordinary default branch can omit it. The reusable workflow does not hardcode `main`; the repository-local [release caller](.github/workflows/release.yml) shows how this repository triggers it.

Release callers keep `release-please-config.json` and `.release-please-manifest.json` at their root, plus a fine-grained `RELEASE_PLEASE_TOKEN` with Contents, Issues, and Pull requests write access. Every package sets `include-v-in-tag: false` and `include-v-in-release-name: false`, either directly or through the config root. The reusable workflow validates this policy before running Release Please. New shared releases use tags without `v`; preserve historical `v` tags and leave the manifest at its current version so the first migrated release creates the next version. Do not delete or duplicate tags. Never use `secrets: inherit`.

### Closed pull request preview cleanup

The caller owns the close trigger and passes `vercel_project`, `vercel_scope`, and its `VERCEL_TOKEN` secret as `vercel_token`. The token should be scoped to the Vercel project. The caller needs `pull-requests: read`; the called workflow reads pull request metadata and GitHub's open pull requests, and does not check out or run pull request code. It checks every page of deployments, removing only those matching the caller repository and PR number after inspecting each deployment's target. If another open pull request shares the branch, it uses Vercel's safe removal mode to protect active aliases.

This workflow is designed for a `pull_request_target` closed trigger because it needs the caller's Vercel token after a PR closes. Keep that caller limited to this reusable workflow, pass only the named Vercel token, and never check out or execute PR code. Pin the reusable workflow to a full commit SHA and update that pin during review.

Public callers should check their GitHub Actions event policy for `pull_request_target`. GitHub plans to enforce a default block on this event on November 2, 2026, unless an applicable policy explicitly allows it. See [GitHub's event policy guidance](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target).

## Permissions and security

Set permissions on the caller job as well as the called workflow. A called workflow cannot increase the caller's token permissions. The quality and dependency-review workflows need `contents: read`; the title and preview cleanup workflows need `pull-requests: read`; release automation needs `contents: write`, `issues: write`, and `pull-requests: write`. The preview cleanup caller uses `pull_request_target` only to process close metadata, never checks out PR code, and passes only its named Vercel token.

Use `pull_request` for normal CI, keep fork jobs read-only, and do not expose secrets to jobs that check out or run pull-request code. Third-party actions are pinned to full SHAs and retain version comments. Review pin changes as executable infrastructure.

## Check names and branch protection

Checks display as `<caller job> / <called job>`. Keep both names stable when they are required by branch protection.

| Caller job | Called job | Required check |
| --- | --- | --- |
| `pr-title` | `Validate title` | `pr-title / Validate title` |
| `bun-quality` | `Install and verify` | `bun-quality / Install and verify` |
| `npm-quality` | `Install and verify` | `npm-quality / Install and verify` |
| `dependency-review` | `Review dependency changes` | `dependency-review / Review dependency changes` |
| `dependabot-auto-merge` | `Enable auto-merge for eligible update` | Not a required check; this workflow requests auto-merge. |

## Performance and local checks

Each shared quality workflow uses one job to install dependencies and run one root `verify` script. npm's setup uses the lockfile-keyed cache provided by `actions/setup-node`. Bun dependency installation currently uses its frozen lockfile without an additional package-store cache; measure CI duration before adding another cache layer.

Use caller-level concurrency to cancel superseded pull-request runs. Keep slow, project-specific checks local and trigger them only for relevant paths when possible; the final `verify` script should still provide one stable required status. For example, Interleaf's QPDF/WASM and browser-fidelity checks remain project-owned.

## Versioning and rollout

Pre-1.0, fixes ship as patches, compatible additions as minors, and breaking changes stay in the 0.x line via a `!` commit. Version 1.0 is reserved for the first stable shared contract, after the portfolio migration is complete and the root contracts and permissions have been exercised across the supported package managers.

See [the portfolio rollout plan](docs/portfolio-rollout.md) for the repository audit, adoption groups, release-tag migration, and proposed PR order. See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [AGENTS.md](AGENTS.md) for contributor and security rules.

## Design references

- [GitHub: reusing workflow configurations](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations) — typed reusable interfaces and caller-to-workflow permission limits.
- [GitHub: securely using `pull_request_target`](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) — why privileged PR workflows must not execute untrusted code.
- [GitHub: Dependabot on Actions](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-on-actions) — Dependabot-triggered token and secret restrictions.
- [GitHub: enabling auto-merge](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-auto-merge-for-pull-requests-in-your-repository) — repository setting required for automatic merges.
- [GitHub Actions reusable workflows](https://github.com/actions/reusable-workflows) — examples organized around specific workflow responsibilities.
- [Release Please action](https://github.com/googleapis/release-please-action) — release metadata and branch targeting.
- [Bun setup action](https://github.com/oven-sh/setup-bun/blob/main/README.md) — supported Bun setup inputs and executable caching.

## License

MIT. See [LICENSE](LICENSE).
