# workflows

Reusable GitHub Actions workflows for [Abijith Suresh](https://github.com/abijith-suresh)'s
repositories. Callers keep their triggers and application-specific checks,
deployment, and publishing logic.

## Adopting a workflow

1. Inspect the caller's existing CI and choose a shared job from
   [.github/workflows/](.github/workflows/). Only files exposing `workflow_call`
   are reusable.
2. Choose a release or reviewed revision, resolve it to a full commit SHA, and
   read the workflow at that SHA. Its declarations, commands, and caller
   comments define what to configure; the current branch may differ.
3. Prepare the required files and service settings. Call the workflow from a
   job's `uses:` field with the full SHA and a version comment. Set needed inputs
   under `with:` and keep event and branch filters in the caller. For other
   project layouts, add a root wrapper or keep the job local.
4. Grant the called jobs' required permissions and pass only declared secrets
   by name. Scope named tokens separately; job permissions govern `GITHUB_TOKEN`.
   Keep ordinary PR CI read-only and free of secrets.
5. Run the caller's checks and lint its workflows. Exercise the intended Actions
   event and confirm check names before updating branch protection. On upgrades,
   review the workflow diff and release notes, then repeat validation.

## Continuous integration

[ci.yml](.github/workflows/ci.yml) is the shared CI for Astro projects: Bun
from the root `mise.toml`, a frozen install, then type check, lint, format
check, tests, build, and the Playwright browser suite as separate steps. There
are no inputs and nothing to configure per project. Every step runs; a missing
or failing script fails the job.

Callers need a root `mise.toml` with a `bun` pin, a `bun.lock` with Playwright,
and `type-check`, `lint`, `format:check`, `test`, `build`, and `test:e2e`
scripts in the root `package.json`. The `test:e2e` script builds the site and
runs Playwright, which owns its preview server through the config. Chromium,
Firefox, and WebKit install with their system dependencies; when the browser
run fails, `test-results/` and `playwright-report/` upload as the
`browser-test-results` artifact.

```yaml
name: CI

on:
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

permissions: {}

jobs:
  ci:
    name: CI
    permissions:
      contents: read
    uses: abijith-suresh/workflows/.github/workflows/ci.yml@FULL_COMMIT_SHA # reviewed revision

  gate:
    name: gate
    if: ${{ !cancelled() }}
    needs: [ci]
    runs-on: ubuntu-24.04
    permissions: {}
    steps:
      - name: Require CI success
        shell: bash
        env:
          CI_RESULT: ${{ needs.ci.result }}
        run: |
          set -euo pipefail
          if [[ "$CI_RESULT" != success ]]; then
            echo "CI result: $CI_RESULT" >&2
            exit 1
          fi
```

Require only the caller's `gate` job in branch protection. It fails when the
pipeline fails and can also cover repository-local jobs; add those jobs to its
`needs` list. Checks inside the call are named
`<caller job name> / <called job name>`; confirm them on a real run before
changing required checks.

### Standard caller set

Projects in the standard setup use the same caller files and job names, all
pinned to the same revision:

| Caller file | Jobs | Extra setup |
|---|---|---|
| `ci.yml` | `ci`, `dependency-review`, `gate` | root `mise.toml`, `bun.lock`, package scripts; dependency review needs a public repository or the licensing for it |
| `pr-title.yml` | `pr-title` | none |
| `dependabot-auto-merge.yml` | `dependabot` | Dependabot config and auto-merge enabled; call from `pull_request_target` with `contents: write` and `pull-requests: write` |
| `release-please.yml` | `release-please` | root release-please config and manifest, `RELEASE_PLEASE_TOKEN` secret |
| `vercel-preview-cleanup.yml` | `cleanup` | Vercel project link; call from `pull_request_target` with `types: [closed]` |

`gate` is a caller-side job that needs the other jobs in `ci.yml` plus any
repository-local jobs; require only `gate` in branch protection. Repository-local
jobs (a qpdf smoke, for example) stay in `ci.yml` so the gate can cover them.
Keep no inline copies of the shared jobs; the shared workflow is the only
implementation.

`ci.yml` replaces `bun-quality.yml` for Astro projects. `npm-quality.yml`
continues for npm projects.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for changes to this repository and
[SECURITY.md](SECURITY.md) to report vulnerabilities.

Published changes appear in [releases](https://github.com/abijith-suresh/workflows/releases)
and the generated [changelog](CHANGELOG.md).

[MIT license](LICENSE).
