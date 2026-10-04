# workflows

Reusable GitHub Actions workflows for [Abijith Suresh](https://github.com/abijith-suresh)'s repositories. Callers choose the triggers and keep project-specific checks, deployment, and publishing in their own repositories.

## Workflow catalog

Call these workflows from a job's `uses:` field:

| Workflow | Use it for | Caller configuration |
| --- | --- | --- |
| [`bun-quality.yml`](.github/workflows/bun-quality.yml) | Install with a frozen Bun lockfile and run the root `verify` script | Root Bun files; no workflow inputs |
| [`npm-quality.yml`](.github/workflows/npm-quality.yml) | Install with `npm ci` and run the root `verify` script | Root npm files; no workflow inputs |
| [`conventional-commit-title.yml`](.github/workflows/conventional-commit-title.yml) | Check a pull request title | No workflow inputs |
| [`dependency-review.yml`](.github/workflows/dependency-review.yml) | Check dependency changes in a pull request | Optional `fail-on-severity` |
| [`dependabot-auto-merge.yml`](.github/workflows/dependabot-auto-merge.yml) | Request auto-merge for eligible Dependabot updates | Optional `major-update-policy` and a named token |
| [`release-please.yml`](.github/workflows/release-please.yml) | Create or update Release Please pull requests | Optional `target-branch`, root metadata, and a named token |
| [`vercel-preview-cleanup.yml`](.github/workflows/vercel-preview-cleanup.yml) | Remove preview deployments when a pull request closes | Vercel project, scope, and a named token |

[`policy.yml`](.github/workflows/policy.yml) validates this repository. [`release.yml`](.github/workflows/release.yml) calls the reusable release workflow for this repository. Neither accepts `workflow_call`.

## Names, pins, and permissions

The examples below pin [release 0.6.0](https://github.com/abijith-suresh/workflows/releases/tag/0.6.0) to its full commit SHA, `163055ac24b4169ae93ae05c5d7491b1cd5d96c7`. Update the SHA when adopting a newer release and retain the release version in a comment. A tag or branch name alone is a mutable reference.

Set `permissions` on each caller job. A reusable workflow cannot increase them. Pass the declared secrets by name, without `secrets: inherit`. Copy input and secret names exactly, including the Vercel workflow's underscores and lowercase `vercel_token`.

| Workflow | Minimum caller job `GITHUB_TOKEN` permissions | Named secret |
| --- | --- | --- |
| Bun quality | `contents: read` | None |
| npm quality | `contents: read` | None |
| Conventional Commit title | `pull-requests: read` | None |
| Dependency review | `contents: read` | None |
| Dependabot auto-merge | `contents: read` and `pull-requests: read` | `DEPENDABOT_AUTOMERGE_TOKEN` |
| Release Please | `contents: write`, `issues: write`, and `pull-requests: write` | `RELEASE_PLEASE_TOKEN` |
| Vercel preview cleanup | `pull-requests: read` | `vercel_token` |

### Required check names

GitHub displays `<caller job name> / <called job name>` for reusable checks. The caller name defaults to its job ID. The workflow's top-level `name:` labels the Actions run. With the examples below:

| Caller job ID | Called job name | Check name |
| --- | --- | --- |
| `bun-quality` | `Install and verify` | `bun-quality / Install and verify` |
| `npm-quality` | `Install and verify` | `npm-quality / Install and verify` |
| `pr-title` | `Validate title` | `pr-title / Validate title` |
| `dependency-review` | `Review dependency changes` | `dependency-review / Review dependency changes` |

Confirm the check name before adding it to branch protection, then keep both job names stable. This repository's policy workflow reports `Validate workflow YAML` and `Conventional Commit title / Validate title`. Dependabot auto-merge requests a merge and should not be a required quality check.

## Quality checks

Choose one package manager workflow. Neither accepts inputs. Both install dependencies and run the caller's root `verify` script. Put package-specific checks in that script. For other layouts, add a root wrapper with the required files or keep the quality job local.

Runtime versions come from the caller's root `mise.toml`. These workflows do not read `packageManager`, `.bun-version`, or `.node-version`; keep any duplicate declarations in sync. Callers can use workflow-level concurrency to cancel superseded pull request runs.

### Bun

The caller needs a root `mise.toml` with one `bun` entry under `[tools]`, pinned to `major.minor.patch`, plus `bun.lock` and `package.json` with a `verify` script:

```toml
[tools]
bun = "1.4.1"
```

```yaml
name: Quality

on:
  pull_request:

permissions: {}

jobs:
  bun-quality:
    uses: abijith-suresh/workflows/.github/workflows/bun-quality.yml@163055ac24b4169ae93ae05c5d7491b1cd5d96c7 # 0.6.0
    permissions:
      contents: read
```

The called job runs `bun install --frozen-lockfile` and `bun run verify`. It adds no package-store cache.

### npm

The caller needs a root `mise.toml` with one `node` and one `npm` entry under `[tools]`, each pinned to `major.minor.patch`, plus `package-lock.json` and `package.json` with a `verify` script:

```toml
[tools]
node = "24.20.0"
npm = "11.16.0"
```

```yaml
name: Quality

on:
  pull_request:

permissions: {}

jobs:
  npm-quality:
    uses: abijith-suresh/workflows/.github/workflows/npm-quality.yml@163055ac24b4169ae93ae05c5d7491b1cd5d96c7 # 0.6.0
    permissions:
      contents: read
```

The called job runs `npm ci` and `npm run verify`. `actions/setup-node` caches npm downloads with a key based on `package-lock.json`.

## Pull request checks

### Conventional Commit title

The title workflow has no inputs. It accepts `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, and `test`, with an optional scope and `!`. The complete title must be at most 72 characters, and the subject must not end in a period. Dependabot titles are exempt.

Include `edited` so a title change reruns the check:

```yaml
name: Pull request title

on:
  pull_request:
    types: [opened, reopened, synchronize, edited]

permissions: {}

jobs:
  pr-title:
    uses: abijith-suresh/workflows/.github/workflows/conventional-commit-title.yml@163055ac24b4169ae93ae05c5d7491b1cd5d96c7 # 0.6.0
    permissions:
      pull-requests: read
```

### Dependency review

The optional `fail-on-severity` input defaults to `high`. Set it to `low`, `moderate`, `high`, or `critical`. This workflow is for public repositories or private repositories with the required GitHub security licensing. Keep project-specific license and scope rules in the caller if needed.

```yaml
name: Pull request dependency review

on:
  pull_request:

permissions: {}

jobs:
  dependency-review:
    uses: abijith-suresh/workflows/.github/workflows/dependency-review.yml@163055ac24b4169ae93ae05c5d7491b1cd5d96c7 # 0.6.0
    with:
      fail-on-severity: high
    permissions:
      contents: read
```

## Dependabot auto-merge

Call this workflow only from `pull_request`. It verifies both the event actor and pull request author are `dependabot[bot]` and never checks out pull request code. GitHub Actions dependency updates always require manual review.

| `major-update-policy` | Eligible updates |
| --- | --- |
| `patch-minor` | Patch and minor updates outside the GitHub Actions ecosystem |
| `compatible-majors` (default) | The above, plus direct development dependency majors and direct production dependency majors with a known compatibility score of at least 90 |

Store a fine-grained token as a Dependabot secret in the caller repository. Limit it to that repository with `Contents: write` and `Pull requests: write`. Dependabot's `GITHUB_TOKEN` is read-only, so the named token requests auto-merge and looks up compatibility scores under `compatible-majors`. Enable auto-merge in repository settings. Required checks and branch protection still apply.

```yaml
name: Dependabot updates

on:
  pull_request:
    types: [opened, reopened, synchronize]

permissions: {}

jobs:
  dependabot-auto-merge:
    if: >-
      github.actor == 'dependabot[bot]' &&
      github.event.pull_request.user.login == 'dependabot[bot]'
    uses: abijith-suresh/workflows/.github/workflows/dependabot-auto-merge.yml@163055ac24b4169ae93ae05c5d7491b1cd5d96c7 # 0.6.0
    with:
      major-update-policy: patch-minor
    permissions:
      contents: read
      pull-requests: read
    secrets:
      DEPENDABOT_AUTOMERGE_TOKEN: ${{ secrets.DEPENDABOT_TOKEN }}
```

Replace `DEPENDABOT_TOKEN` with the caller's Dependabot secret name. Omit `major-update-policy` to use the default `compatible-majors` policy.

## Release Please

Provide root `release-please-config.json` and `.release-please-manifest.json` files and a fine-grained `RELEASE_PLEASE_TOKEN`. Set `include-v-in-tag` and `include-v-in-release-name` to `false` for every package, or at the config root. The workflow validates these settings and runs only for branch `push` and `workflow_dispatch` events.

The caller chooses its triggers and release branches. `target-branch` defaults to the triggering branch. For multiple release branches, pass `${{ github.ref_name }}` and filter manual dispatches too:

```yaml
name: Release automation

on:
  push:
    branches: [main, 1.x]
  workflow_dispatch:

permissions: {}

jobs:
  release-please:
    if: >-
      github.ref_type == 'branch' &&
      (github.ref_name == 'main' || github.ref_name == '1.x')
    uses: abijith-suresh/workflows/.github/workflows/release-please.yml@163055ac24b4169ae93ae05c5d7491b1cd5d96c7 # 0.6.0
    with:
      target-branch: ${{ github.ref_name }}
    permissions:
      contents: write
      issues: write
      pull-requests: write
    secrets:
      RELEASE_PLEASE_TOKEN: ${{ secrets.RELEASE_PLEASE_TOKEN }}
```

A single-branch caller can omit `with: target-branch`. Give the token only the listed write permissions. New releases use tags without `v`; preserve historical `v` tags and keep the manifest at its current version when migrating. This repository's [local release caller](.github/workflows/release.yml) shows the default-branch setup.

## Vercel preview cleanup

Use a dedicated caller for `pull_request_target` with `types: [closed]`. Pass the Vercel project and team slug. Map a token for that team to `vercel_token`; its owner needs permission to list, inspect, and remove the project's deployments.

The job checks repository and PR metadata and the deployment target before removal. It never checks out or executes pull request code. If an open pull request shares the head branch, it uses `vercel rm --safe` to protect active aliases.

The 0.6.0 pin below lacks two later safeguards: the job's closed-PR guard and isolation of tokens from CLI installation. Update the pin to a release containing those changes before relying on them. The example's event filter already limits calls to closed pull requests.

```yaml
name: Vercel preview cleanup

on:
  pull_request_target:
    types: [closed]

permissions: {}

jobs:
  vercel-preview-cleanup:
    uses: abijith-suresh/workflows/.github/workflows/vercel-preview-cleanup.yml@163055ac24b4169ae93ae05c5d7491b1cd5d96c7 # 0.6.0
    with:
      vercel_project: my-project
      vercel_scope: my-team
    permissions:
      pull-requests: read
    secrets:
      vercel_token: ${{ secrets.VERCEL_TOKEN }}
```

Keep that privileged caller limited to this workflow and its named token. For public repositories, check the applicable Actions event policy: [GitHub plans to enforce its default block on `pull_request_target` on November 2, 2026](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) unless a policy explicitly allows the event.

## Maintenance and releases

Before 1.0, fixes ship as patches, compatible additions as minors, and breaking interface changes stay in the 0.x line via a `!` commit. Publish interface changes with a versioned release, then update consumer pins to the new immutable SHA and update required check names if they changed. See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [AGENTS.md](AGENTS.md) for repository guidance.

## References

- [GitHub: Reuse workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) explains caller jobs, inputs, and secrets.
- [GitHub: Reusing workflow configurations](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations) covers permission limits and supported caller job keys.
- [GitHub: Securely using `pull_request_target`](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) explains the privileged event.
- [GitHub: Dependabot on Actions](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-on-actions) covers Dependabot-triggered token and secret restrictions.
- [GitHub: Enabling auto-merge](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-auto-merge-for-pull-requests-in-your-repository) covers the repository setting.
- [Vercel: API access tokens](https://vercel.com/kb/guide/how-do-i-use-a-vercel-api-access-token) explains team token scopes.

## License

MIT. See [LICENSE](LICENSE).
