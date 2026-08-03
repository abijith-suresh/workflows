# workflows

This repository has two purposes:

1. reusable GitHub Actions workflows for [Abijith Suresh](https://github.com/abijith-suresh)'s repositories; and
2. a small, transparent learning and reference project for designing safe,
   maintainable workflows.

It is intentionally not a general-purpose CI platform. Application-specific
build, deploy, release, publishing, and environment policy stay in the
consuming repository.

## Workflows

- [`bun-quality.yml`](.github/workflows/bun-quality.yml) installs a caller's
  Bun dependencies and runs its verification command.
- [`dependency-review.yml`](.github/workflows/dependency-review.yml) reviews
  dependency changes in a pull request without installing or running project
  code.
- [`pr-title.yml`](.github/workflows/pr-title.yml) checks a pull request title
  against the supported Conventional Commit format.
- [`policy.yml`](.github/workflows/policy.yml) is repository-local validation:
  it runs `actionlint` on the workflow YAML and calls `pr-title.yml` for pull
  requests. It does not provide application CI.

## Calling a reusable workflow

A caller owns the event trigger and delegates one job to this repository. Pin
that job to a full commit SHA; the version comment is a readable upgrade hint,
not the security boundary. These examples use the current `main` workflow
baseline: `0.0.1` is the current released baseline, and `0.1.0` is pending this
release PR. After PR #6 is merged and its release is created, replace the pins
with the final released commit SHA and update the comments.

```yaml
name: Quality

on:
  pull_request:

permissions:
  contents: read

jobs:
  bun-quality:
    uses: abijith-suresh/workflows/.github/workflows/bun-quality.yml@d47573a18810d3ce069939b683a8d7eaa7304267 # current main baseline; replace with the 0.1.0 release commit SHA after PR #6
    with:
      working-directory: .
      verify-command: bun run verify
    permissions:
      contents: read
```

```yaml
name: Pull request title

on:
  pull_request:

permissions:
  pull-requests: read

jobs:
  pr-title:
    uses: abijith-suresh/workflows/.github/workflows/pr-title.yml@d47573a18810d3ce069939b683a8d7eaa7304267 # current main baseline; replace with the 0.1.0 release commit SHA after PR #6
    permissions:
      pull-requests: read
```

```yaml
name: Dependency review

on:
  pull_request:

permissions:
  contents: read

jobs:
  dependency-review:
    uses: abijith-suresh/workflows/.github/workflows/dependency-review.yml@d47573a18810d3ce069939b683a8d7eaa7304267 # current main baseline; replace with the 0.1.0 release commit SHA after PR #6
    with:
      fail-on-severity: high
    permissions:
      contents: read
```

`dependency-review.yml` reviews dependency diffs through GitHub's dependency
graph; it does not install Bun or npm dependencies or run project scripts. Keep
quality and build workflows separate in the consuming repository.

Reusable workflows are jobs, not steps: a job using `uses` cannot also define
`runs-on` or `steps`. See GitHub's
[reusable workflow documentation](https://docs.github.com/en/actions/sharing-automations/reusing-workflows).

### `bun-quality.yml` inputs

| Input | Required | Default | Purpose |
| --- | --- | --- | --- |
| `working-directory` | No | `.` | Bun project directory. |
| `verify-command` | No | `bun run verify` | Command run after `bun install --frozen-lockfile`. |

The Bun workflow checks out the caller repository, uses its `.bun-version`
when present (otherwise the latest Bun release), installs dependencies, and
runs the configured command. It therefore executes caller-controlled code.

### `dependency-review.yml` inputs

| Input | Required | Default | Purpose |
| --- | --- | --- | --- |
| `fail-on-severity` | No | `high` | Fails when a dependency diff introduces a vulnerability at or above this severity. |

The supported values are `low`, `moderate`, `high`, and `critical`.

### Permissions and security

- Grant only the permissions the called workflow needs: `contents: read` for
  `bun-quality.yml` and `dependency-review.yml`, or `pull-requests: read` for
  `pr-title.yml`. Dependency review does not post pull request comments.
- Use `pull_request`, not `pull_request_target`, when a workflow checks pull
  request code. Keep fork jobs read-only and do not pass secrets to them.
- These reusable workflows require no repository secrets. Do not use
  `secrets: inherit` unless a separately reviewed workflow genuinely needs it.
- All third-party actions in this repository are pinned to full commit SHAs.
  Review pin changes as executable CI changes.

## What stays local to callers

Consuming repositories choose their own triggers, application tests and build
matrices, deployments, environments and approvals, secrets, publishing, and
application-specific release automation. Branch protection is a repository
setting, and releases are tags/GitHub releases or release workflows; neither
is implicitly provided to consuming repositories by these reusable workflows.

## Versioning and learning notes

Until a stable `1.x` line is intentionally declared, this project follows a
pre-1.0 maturity policy: release-worthy fixes and maintenance changes use
patch releases, while meaningful additions use minor releases. Breaking
interface changes before 1.0.0 remain in the 0.x line; use a new major version
only after a stable 1.x line has been declared. Callers should continue to pin
the full commit SHA and keep the release in a comment. Document input,
permission, and security changes alongside the implementation.

The repository's own GitHub Actions dependencies are checked weekly by
Dependabot. For contribution and security guidance, see
[CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and
[AGENTS.md](AGENTS.md).

## Automated releases

Release Please runs in manifest mode from `.github/workflows/release-please.yml`
on pushes to `main` (and manually through `workflow_dispatch`; it does not run
on pull requests). It opens or updates one release PR containing changes to
`CHANGELOG.md`, `VERSION`, and `.release-please-manifest.json`. After that
release PR is merged, Release Please creates the corresponding SemVer tag and
GitHub Release.

The mistaken `v1.0.0` tag was deleted. `0.0.1` is the current released
baseline, and `0.1.0` is pending this release PR. Its corresponding SemVer tag
and GitHub Release will be created only after PR #6 is merged. The manifest and
`VERSION` file in this PR both record `0.1.0`; the simple strategy is configured
to use `VERSION`, and component names are omitted so future tags continue to be
generated without a component prefix.

Before relying on releases, a maintainer must add a fine-grained token as the
repository Actions secret `RELEASE_PLEASE_TOKEN`. Do not commit a token or
create an empty placeholder. The token should be limited to this repository
with only the permissions Release Please needs: **Contents: read and write**,
**Issues: read and write**, and **Pull requests: read and write** (repository
metadata read is required automatically). No repository secret or setting is
managed by this repository. If repository policy requires it, a maintainer
must also allow GitHub Actions to create pull requests; that setting is
intentionally not changed here.

Use the existing pull-request title policy for changes that affect releases:

- `fix:` (including `fix(ci): ...`) produces a patch release for fixes and
  release-worthy maintenance.
- `feat:` (including `feat(ci): ...`) produces a minor release for meaningful
  additions.
- Before 1.0.0, any type with `!` or a `BREAKING CHANGE` footer uses Release
  Please's `bump-minor-pre-major` setting and stays in the 0.x line instead of
  creating a 1.0.0/major release.
- A workflow behavior change should use `feat(ci): ...` when it adds a
  capability, `fix(ci): ...` when correcting behavior, or the corresponding
  `!` form when it breaks a caller. Use `ci:` or `chore:` for non-release-
  worthy maintenance.

## License

MIT. See [LICENSE](LICENSE).
