# workflows — agent brief

Reusable GitHub Actions workflows that standard-setup repositories call by pinned revision;
this brief is for anyone changing this library.

## The Project
Core promise: one reviewed home for shared CI, release, and repository-maintenance jobs, so
callers keep only their triggers and application-specific logic.
Non-goals: not an app or runtime library; no end-user docs; caller-specific checks, deployment,
and publishing stay in the caller.
Status: live (maintenance) — consumed by repositories in the standard setup through tagged
revisions.

## How I Work Here
- Quality gate: run `actionlint` and `git diff --check` from the repo root before handoff; there
  is no unit-test suite. `.github/workflows/policy.yml` is the authority for validation commands
  and tool versions.
- Commits: Conventional Commits; accepted types and title limits live in
  `.github/workflows/conventional-commit-title.yml`. Squash merges; never commit to main.
- Interfaces and executable rules live in YAML. Markdown covers purpose and process only — never
  a parallel catalog or a copy of workflow rules.
- Called workflows check out the caller, so helper scripts in this repository are not available
  to their jobs. That is why quality workflows require a caller-side root verification script.
- Preserve public input, secret, and check names unless the change includes a caller migration plan.
- Pin third-party actions to full SHAs with version comments; grant permissions per job; pass only
  named secrets; keep privileged jobs away from untrusted PR code.
- Do not add arbitrary command or directory inputs to quality workflows.
- Before 1.x, breaking changes use `!` and a 0.x minor release. Release metadata manages versions,
  tags, and the changelog; tags carry no `v` prefix.

## Sources of Truth
| Fact | Where |
|---|---|
| Product intent | § The Project (this file) |
| Runtime behavior | `.github/workflows/*.yml` |
| Validation commands & tool versions | `.github/workflows/policy.yml` |
| Version & release metadata | `VERSION`, `release-please-config.json`, `.release-please-manifest.json` |
| Commit rules | `.github/workflows/conventional-commit-title.yml` |

Workflow YAML and repository policy CI are the authority; this file never overrides executable truth.

## Getting Around
Only files exposing `workflow_call` are reusable; `policy.yml` and `release.yml` are this
repository's own callers.
- `.github/workflows/ci.yml` — shared Astro CI: Bun from root `mise.toml`, frozen install, then type-check, lint, format:check, test, build, and Playwright (Chromium/Firefox/WebKit).
- `.github/workflows/bun-quality.yml` — Bun projects: validates the single root mise.toml Bun pin, installs, runs `bun run verify`.
- `.github/workflows/npm-quality.yml` — npm projects: validates root mise.toml node/npm pins, installs that exact npm, runs `npm run verify`.
- `.github/workflows/release-please.yml` — reusable Release Please; needs caller config/manifest and a `RELEASE_PLEASE_TOKEN`, enforces the no-`v` tag policy.
- `.github/workflows/conventional-commit-title.yml` — validates PR titles against Conventional Commits.
- `.github/workflows/dependency-review.yml` — reviews dependency changes on pull requests.
- `.github/workflows/dependabot-auto-merge.yml` — enables auto-merge for eligible Dependabot updates.
- `.github/workflows/vercel-preview-cleanup.yml` — removes Vercel preview deployments when a pull request closes.
- `.github/workflows/policy.yml` — repo-local policy CI (actionlint, whitespace, release metadata).
- `.github/workflows/release.yml` — repo-local caller that runs Release Please on main.
- `CONTRIBUTING.md` — how to change this repository; `README.md` — adoption process and the standard caller set.
