# Contributing

1. Read the affected workflow and its callers. Keep reusable jobs small and
   project-specific logic in consumers. Preserve public input, secret, and check
   names unless the change includes a migration plan. Quality workflows keep a
   root verification script; do not add arbitrary command or directory inputs.
2. Put interfaces and executable rules in YAML. Use comments for caller setup
   or tradeoffs the code cannot explain. Markdown covers purpose and process,
   without parallel catalogs or copies of workflow rules. Called workflows
   check out the caller, so helper scripts in this repository are unavailable
   to their jobs.
3. Review workflows and dependency updates as executable code. Pin third-party
   actions to full SHAs with version comments and verify them against official
   upstream release tags. Grant permissions per job, pass only named secrets,
   and isolate privileged jobs from untrusted PR code.
4. Run `git diff --check` and `actionlint` from the root before handoff, and
   validate changed JSON. There is no `package.json` or unit-test suite — do not
   invent a `verify` script. [policy.yml](.github/workflows/policy.yml) owns the
   exact commands and tool versions, and policy CI is the final gate for
   workflows in this repository.
5. Use Conventional Commits for commits and the PR title, following
   [conventional-commit-title.yml](.github/workflows/conventional-commit-title.yml).
   Explain behavior changes, validation, checks you could not run, and caller
   migration steps. Before stable 1.x, breaking changes use `!` and a 0.x minor
   release.
6. Never commit straight to main. Squash-merge once approved, and leave PRs open
   for owner review rather than merging them yourself. [CHANGELOG.md](CHANGELOG.md),
   `VERSION`, and release tags are written by release-please from Conventional
   Commits — never hand-edit them.
