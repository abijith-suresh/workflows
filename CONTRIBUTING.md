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
4. Follow [policy.yml](.github/workflows/policy.yml) for validation commands and
   tool versions. Run `git diff --check` and `actionlint` from the root. Validate
   changed YAML and JSON, use any configured formatter, and inspect the parsed
   YAML and final diff. Keep policy CI focused on this repository's workflows.
5. Use the rules in
   [conventional-commit-title.yml](.github/workflows/conventional-commit-title.yml)
   for the PR title. Explain behavior changes, validation, checks you could not
   run, and caller migration steps. Before stable 1.x, breaking changes use `!`
   and a 0.x minor release. Let [release.yml](.github/workflows/release.yml) and
   release metadata manage versions, tags, and the changelog.
