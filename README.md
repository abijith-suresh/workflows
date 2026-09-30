# workflows

Reusable GitHub Actions workflows for [Abijith Suresh](https://github.com/abijith-suresh)'s repositories. Each workflow has a narrow caller contract; the consuming repository owns its triggers, project-specific checks, and deployment or publishing steps.

## Workflow catalog

These seven files expose `workflow_call` and can be called by other repositories:

| Workflow | Use it for | Caller configuration |
| --- | --- | --- |
| [`bun-quality.yml`](.github/workflows/bun-quality.yml) | Install with a frozen Bun lockfile and run the root `verify` script | Root Bun files; no workflow inputs |
| [`npm-quality.yml`](.github/workflows/npm-quality.yml) | Install with `npm ci` and run the root `verify` script | Root npm files; no workflow inputs |
| [`conventional-commit-title.yml`](.github/workflows/conventional-commit-title.yml) | Check a pull request title | No workflow inputs |
| [`dependency-review.yml`](.github/workflows/dependency-review.yml) | Check dependency changes in a pull request | Optional `fail-on-severity` |
| [`dependabot-auto-merge.yml`](.github/workflows/dependabot-auto-merge.yml) | Request auto-merge for eligible Dependabot updates | Optional `major-update-policy` and a named token |
| [`release-please.yml`](.github/workflows/release-please.yml) | Create or update Release Please pull requests | Optional `target-branch`, root metadata, and a named token |
| [`vercel-preview-cleanup.yml`](.github/workflows/vercel-preview-cleanup.yml) | Remove preview deployments when a pull request closes | Vercel project, scope, and a named token |

[`policy.yml`](.github/workflows/policy.yml) and [`release.yml`](.github/workflows/release.yml) run only in this repository. They are examples of a local policy workflow and a local caller of the reusable release workflow; neither is a public `workflow_call` interface.

The workflow files are the executable source of truth. This guide explains their caller contracts and shows examples pinned to a published release.

## Names, pins, and permissions

Workflow filenames use lowercase kebab-case. A caller invokes a reusable workflow in a job with `uses:`, not in a step. Use a stable caller job ID such as `bun-quality` or `pr-title`. The caller workflow's top-level `name:` labels the Actions run; the caller job and the called job determine the check name.

For a reusable job, GitHub displays `<caller job display name> / <called job display name>`. If the caller sets a job `name:`, it replaces the caller job ID in that display. For example, this repository's policy caller sets `name: Conventional Commit title`, so its check is `Conventional Commit title / Validate title`. Confirm the observed check before adding it to branch protection, and keep both job names stable afterward.

The examples below pin [release 0.6.0](https://github.com/abijith-suresh/workflows/releases/tag/0.6.0) to its full commit SHA, `163055ac24b4169ae93ae05c5d7491b1cd5d96c7`. Update the SHA when adopting a newer release and retain the release version in a comment. A tag or branch name alone is a mutable reference.

Set the caller job's `permissions` explicitly. A reusable workflow cannot increase the permissions granted by its caller. Pass only the named secrets each workflow declares; do not use `secrets: inherit` for these examples. Input and secret identifiers are part of the callable interface, so copy their spelling exactly. The Vercel workflow currently uses underscores and a lowercase secret identifier.

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

With the example caller job IDs below and no caller job `name:`, the reusable checks appear as follows:

| Caller job ID | Called job name | Check name |
| --- | --- | --- |
| `bun-quality` | `Install and verify` | `bun-quality / Install and verify` |
| `npm-quality` | `Install and verify` | `npm-quality / Install and verify` |
| `pr-title` | `Validate title` | `pr-title / Validate title` |
| `dependency-review` | `Review dependency changes` | `dependency-review / Review dependency changes` |

Dependabot auto-merge requests a merge; it is not a required quality check. On pull requests, this repository's local policy workflow reports `Validate workflow YAML` and `Conventional Commit title / Validate title`.

## Quality checks

Choose **one** package manager workflow. Both are zero-input root contracts: they install dependencies and run only the caller's root `verify` script. Package-specific checks can be called by that script. A different project layout can expose the root contract with a compatibility wrapper or keep its quality job local.

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

The called job runs `bun install --frozen-lockfile` and `bun run verify`.

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

The called job runs `npm ci` and `npm run verify`. Both quality workflows read runtime versions from the checked-out caller's root `mise.toml`, not from this repository, `packageManager`, `.bun-version`, or `.node-version`. Reconcile duplicate runtime declarations in the caller.

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

Store a fine-grained token as a **Dependabot secret** in the caller repository. Scope it to that repository with `Contents: write` and `Pull requests: write`. Dependabot-triggered `GITHUB_TOKEN` permissions are read-only; the named token requests auto-merge and, under `compatible-majors`, looks up compatibility scores. Enable auto-merge in repository settings; required checks and branch protection still gate merging.

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

Change `major-update-policy` to `compatible-majors` to use that policy. Replace `DEPENDABOT_TOKEN` with the caller's Dependabot secret name.

## Release Please

The caller owns its push and manual triggers, release branch filters, root `release-please-config.json` and `.release-please-manifest.json`, and a fine-grained `RELEASE_PLEASE_TOKEN`. Every package must set `include-v-in-tag` and `include-v-in-release-name` to `false`, directly or at the config root. The reusable workflow validates those settings and runs only for branch `push` and `workflow_dispatch` events. It never hardcodes `main`.

The optional `target-branch` input defaults to the triggering branch. For more than one release branch, pass `${{ github.ref_name }}` and filter manual dispatches too:

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

Use a dedicated caller for the `pull_request_target` `closed` event. Pass the exact Vercel project and team scope. Create a Vercel access token scoped to the team that owns the project and map it to the required `vercel_token` secret. The token owner needs access to list, inspect, and remove that project's deployments. The called job reads pull request metadata and open pull requests, checks deployment metadata and target before removal, and does not check out or execute pull request code. If another open pull request shares the head branch, it uses safe removal to protect active aliases.

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

The quality workflows use one stable root `verify` entry point. npm uses the lockfile-keyed `actions/setup-node` cache; Bun currently has no extra package-store cache. Callers can cancel superseded pull request runs with caller-level concurrency and keep application-specific smoke, browser, deployment, and publishing jobs local.

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
