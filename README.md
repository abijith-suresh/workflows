# workflows

Reusable GitHub Actions workflows and default repository configuration for
[Abijith Suresh](https://github.com/abijith-suresh)'s repositories. Callers keep
their triggers and application-specific checks, deployment, and publishing
logic.

## Adopting a workflow

1. Inspect the caller's existing CI and choose a shared job from
   [.github/workflows/](.github/workflows/). Only files exposing `workflow_call`
   are reusable.
2. Choose a release, resolve its tag to a full commit SHA, and read the workflow
   at that SHA. Its declarations, commands, and caller comments define what to
   configure; the current branch may differ.
3. Start from the matching caller file in [templates/](templates/). Replace each
   `FULL_COMMIT_SHA # vX.Y.Z` with the chosen SHA and its exact tag. Pin every
   reference to this repository at the same release. Keep event and branch
   filters in the caller. For other project layouts, add a root wrapper or keep
   the job local.
4. Grant the called jobs' required permissions and pass only declared secrets
   by name. Scope named tokens separately; job permissions govern `GITHUB_TOKEN`.
   Keep ordinary PR CI read-only and free of secrets.
5. Run the caller's checks and lint its workflows. Exercise the intended Actions
   event and confirm check names before updating branch protection. On upgrades,
   review the workflow diff and release notes, then repeat validation.
   Dependabot's `github-actions` ecosystem proposes pin updates; auto-merge
   skips that ecosystem, so each one gets a human review.

## Standard caller set

Projects in the standard setup copy these caller files from
[templates/.github/workflows/](templates/.github/workflows/), with the same file
and job names:

| Caller file | Jobs | Extra setup |
|---|---|---|
| `ci.yml` | `ci`, `dependency-review`, `gate` | root `mise.toml`, `bun.lock`, package scripts; dependency review needs a public repository or the licensing for it |
| `pr-title.yml` | `pr-title` | none |
| `dependabot-auto-merge.yml` | `dependabot` | Dependabot config and auto-merge enabled in repository settings |
| `release-please.yml` | `release-please` | root release-please config and manifest, `RELEASE_PLEASE_TOKEN` secret |
| `vercel-preview-cleanup.yml` | `cleanup` | Vercel project link, `VERCEL_TOKEN` secret |

Require exactly two checks in branch protection: `gate` and
`pr-title / Validate title`. `gate` runs the
[gate action](.github/actions/gate/action.yml), which fails unless every job
in its `needs` succeeded. Repository-local jobs (a qpdf smoke, for example) go
in `ci.yml` and in the gate's `needs`. Keep no inline copies of the shared jobs.
The shared workflow is the only implementation.

## Continuous integration

[ci.yml](.github/workflows/ci.yml) is the shared CI for Astro projects: Bun
from the root `mise.toml`, a frozen install, then type check, lint, format
check, tests, build, and the Playwright browser suite as separate steps. There
are no inputs. Every step runs; a missing or failing script fails the job.

The Build step runs before the browser suite, and `test:e2e` consumes that
build: it runs Playwright, which owns its preview server through the config,
without building again. For a clean local run, callers can add a
`test:e2e:build` script that runs `bun run build && bun run test:e2e`; CI does
not call it. When the browser run fails, `test-results/` and
`playwright-report/` upload as the `browser-test-results` artifact.

Bun projects without a browser suite use
[bun-quality.yml](.github/workflows/bun-quality.yml), and npm projects use
[npm-quality.yml](.github/workflows/npm-quality.yml). Both run the root
`verify` script.

## Shared defaults

[templates/](templates/) mirrors where each file goes in a consumer:

| File | Default |
|---|---|
| `mise.toml` | the only tool version source, exact versions |
| `.github/dependabot.yml` | weekly grouped minor and patch updates for the package manager and for GitHub Actions |
| `release-please-config.json`, `.release-please-manifest.json` | single `node` package; before 1.0, features bump the patch and breaking changes the minor; default `v` tags |
| `commitlint.config.ts` | the same types, length, and full-stop rules as the PR title check |
| `biome.json` | formatter, recommended lint preset, Markdown and Astro overrides |

Copy a default, then change it only where the project needs to. Keep
project-specific Biome rule overrides beside the shared base.

## Releases and tags

Single-package repositories release with release-please and tag `vX.Y.Z`, the
release-please default. The shared [release-please.yml](.github/workflows/release-please.yml)
rejects configurations that turn the prefix off. Workspaces that publish
several packages with Changesets keep its `<package>@<version>` tags. This
repository follows the same standard; releases 0.5.0 through 0.8.1 carry both
the unprefixed tag they were cut with and a matching `v` tag.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for changes to this repository and
[SECURITY.md](SECURITY.md) to report vulnerabilities.

Published changes appear in [releases](https://github.com/abijith-suresh/workflows/releases)
and the generated [changelog](CHANGELOG.md).

[MIT license](LICENSE).
