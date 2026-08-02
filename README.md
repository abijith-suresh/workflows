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
- [`pr-title.yml`](.github/workflows/pr-title.yml) checks a pull request title
  against the supported Conventional Commit format.
- [`policy.yml`](.github/workflows/policy.yml) is repository-local validation:
  it runs `actionlint` on the workflow YAML and calls `pr-title.yml` for pull
  requests. It does not provide application CI.

## Calling a reusable workflow

A caller owns the event trigger and delegates one job to this repository. Pin
that job to a full commit SHA; the version comment is a readable upgrade hint,
not the security boundary. These examples use the `v1.0.0` commit currently
published by this repository:

```yaml
name: Quality

on:
  pull_request:

permissions:
  contents: read

jobs:
  bun-quality:
    uses: abijith-suresh/workflows/.github/workflows/bun-quality.yml@1cc4c98be2c52b9731c7ec3023f4ebad2b41d8a6 # v1.0.0
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
    uses: abijith-suresh/workflows/.github/workflows/pr-title.yml@1cc4c98be2c52b9731c7ec3023f4ebad2b41d8a6 # v1.0.0
    permissions:
      pull-requests: read
```

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

### Permissions and security

- Grant only the permissions the called workflow needs: `contents: read` for
  `bun-quality.yml`, or `pull-requests: read` for `pr-title.yml`.
- Use `pull_request`, not `pull_request_target`, when a workflow checks pull
  request code. Keep fork jobs read-only and do not pass secrets to them.
- Neither reusable workflow requires repository secrets. Do not use
  `secrets: inherit` unless a separately reviewed workflow genuinely needs it.
- All third-party actions in this repository are pinned to full commit SHAs.
  Review pin changes as executable CI changes.

## What stays local to callers

Consuming repositories choose their own triggers, application tests and build
matrices, deployments, environments and approvals, secrets, publishing, and
release automation. Branch protection is a repository setting, and releases
are tags/GitHub releases or release workflows; neither is implicitly provided
by these reusable workflows.

## Versioning and learning notes

After review, reusable interface changes can be published with a versioned tag
or GitHub release. Callers should continue to pin the full commit SHA and keep
the release in a comment. Use a new major version for breaking interface
changes, and document input, permission, and security changes alongside the
implementation.

The repository's own GitHub Actions dependencies are checked weekly by
Dependabot. For contribution and security guidance, see
[CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and
[AGENTS.md](AGENTS.md).

## License

MIT. See [LICENSE](LICENSE).
