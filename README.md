# workflows

Reusable GitHub Actions workflows for [abijith-suresh](https://github.com/abijith-suresh)'s repositories.

This repository is intentionally small: it provides shared workflow infrastructure, not a general-purpose CI platform. The initial supported scope is:

- quality checks for Bun-based frontend projects; and
- Conventional Commit-style pull request title validation.

Application-specific build, deploy, release, and publishing workflows remain in each application repository for now. They need their own domain knowledge, environments, approvals, and permissions.

## Calling a reusable workflow

A caller adds a normal workflow triggered by its own events, then delegates a job to this repository. Pin the reusable workflow to a full commit SHA and keep the version as a comment so upgrades are deliberate:

```yaml
name: Quality

on:
  pull_request:

permissions:
  contents: read

jobs:
  bun-quality:
    uses: abijith-suresh/workflows/.github/workflows/bun-quality.yml@<40-character-commit-sha> # v1.0.0
    with:
      working-directory: .
      verify-command: bun run verify
    permissions:
      contents: read
```

The PR-title workflow is called in the same way:

```yaml
name: Pull request title

on:
  pull_request:

permissions:
  pull-requests: read

jobs:
  pr-title:
    uses: abijith-suresh/workflows/.github/workflows/pr-title.yml@<40-character-commit-sha> # v1.0.0
    permissions:
      pull-requests: read
```

Reusable workflows are jobs, not steps: a job that uses `uses` cannot also define `runs-on` or `steps`. The calling workflow chooses the trigger, while the called workflow supplies the implementation. See GitHub's [reusable workflow documentation](https://docs.github.com/en/actions/sharing-automations/reusing-workflows).

## Security and permissions

- Call these workflows from `pull_request`, rather than `pull_request_target`, when checking pull request code. The Bun workflow checks out and executes code from the caller repository.
- Grant only the permissions needed by the called workflow. The Bun workflow needs `contents: read`; the title check needs `pull-requests: read`. A called workflow cannot elevate the caller's permissions.
- Neither workflow accepts, reads, or requires repository secrets. Do not add `secrets: inherit` unless a future workflow has an explicitly reviewed need.
- The Bun workflow runs dependency installation and the caller's verification command. Treat those commands as untrusted code for fork pull requests: use read-only permissions and do not make secrets available.
- Third-party actions are pinned to full commit SHAs in this repository. Review action changes before updating those pins.

## Versioning and upgrades

Consumers should use a full 40-character commit SHA, with the corresponding release or version tag in a comment. Tags are convenient labels, not a replacement for SHA pinning. Updates should be reviewed as changes to executable CI infrastructure, then adopted by changing the SHA in each caller. Breaking interface changes should use a new major version; the initial interface is the `v1` line.

The repository's own GitHub Actions dependencies are checked weekly by Dependabot. Minor and patch updates are grouped; major updates stay separate for explicit human review.

## Available workflows

### `bun-quality.yml`

Runs in the caller repository and:

1. checks out the caller repository;
2. reads `<working-directory>/.bun-version` when that file exists, otherwise installs the latest Bun release;
3. runs `bun install --frozen-lockfile`; and
4. runs the configured verification command.

Inputs:

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `working-directory` | No | `.` | Directory containing the Bun project. |
| `verify-command` | No | `bun run verify` | Command used to verify the project after installation. |

### `pr-title.yml`

Checks the pull request title against this format:

```text
<type>[optional(scope)][optional !]: <description>
```

Supported types are `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, and `test`. For example, `feat(ui): add keyboard navigation` and `fix!: remove the legacy API` are valid. The description must be non-empty and separated from the prefix by `: `.

Dependabot pull requests are exempt based on the pull request author's account (`dependabot[bot]`). This keeps automated dependency and security updates from being blocked by their standard `Bump ...` titles; human-authored pull requests still need a Conventional Commit title.

## Development

This repository contains workflow YAML rather than an application. Make focused changes, inspect the rendered YAML, and run a workflow linter such as `actionlint` before opening a pull request when it is available.

## License

MIT. See [LICENSE](LICENSE).
