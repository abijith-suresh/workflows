# workflows — agent brief

## The Project
A central library of reusable GitHub Actions workflows. Standard-setup repositories call them
by pinned revision for shared CI, release, and repository maintenance, while keeping their own
triggers and application-specific checks, deployment, and publishing logic.

Non-goals: this is not an app, runtime library, or end-user product; caller-specific CI,
deployment, and publishing stay in the caller. Status: live (maintenance).

## How I Work Here
- Interfaces and executable rules live in YAML. Markdown covers purpose and process only —
  never a parallel catalog or a copy of workflow rules.
- Preserve reusable workflows' input, secret, and check names unless the change includes a
  caller migration plan.
- Called workflows check out the caller, so helper scripts in this repository are unavailable
  to their jobs. Quality workflows therefore depend on a caller-side root verification script;
  do not add arbitrary command or directory inputs to them.
- Third-party actions stay pinned to full SHAs with version comments; grant permissions per
  job; pass only named secrets; keep privileged jobs away from untrusted PR code.
- Commits: Conventional Commits; the accepted types live in
  `.github/workflows/conventional-commit-title.yml`. Squash merges; never commit to main.
- Verification: validate changed YAML locally; `.github/workflows/policy.yml` owns the exact
  commands and tool versions and is the final gate. There is no unit-test suite — do not
  invent a `verify` script.

## Sources of Truth
| Fact | Where |
|---|---|
| Product intent | § The Project (this file) |
| Runtime behavior | `.github/workflows/*.yml` |
| Validation commands & tool versions | `.github/workflows/policy.yml` |
| Version & release metadata | `VERSION`, `release-please-config.json`, `.release-please-manifest.json` |
| Commit & title rules | `.github/workflows/conventional-commit-title.yml` |

Code and tests are the authority; this file never overrides executable truth.
