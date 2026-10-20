# workflows — agent brief

Reusable GitHub Actions workflows for the owner's repositories. Callers pin a revision for shared CI, release, and repository maintenance while keeping their own triggers, application-specific checks, deployment, and publishing.

## The Project
Core promise: one shared implementation of standard repository setup, adopted by full-SHA pin, so callers get identical behavior and can audit exactly what runs.
Philosophy: executable truth lives in YAML. Workflows declare their own contract; prose explains purpose and adoption and never restates the rules.
Non-goals: an app, runtime library, or end-user product; caller-specific triggers, deployment, and publishing stay in the caller.
Status: live (maintenance).

## Sources of Truth
| Fact | Where |
|---|---|
| Product intent | this file |
| Runtime behavior | `.github/workflows/*.yml` |
| Commands & deps | no package.json — `actionlint`; `policy.yml` owns exact commands and versions |
| How to work here | CONTRIBUTING.md |
| Adoption | README.md § Adopting a workflow |
| Version & release metadata | `VERSION`, `release-please-config.json`, `.release-please-manifest.json` |

Code and tests are the authority; this file never overrides executable truth.
