# Working with these workflows

Use the appropriate path below, whether you are changing this repository or
adopting a workflow elsewhere. Follow the target repository's own instructions
as well.

## Adopting a workflow

1. Inspect the caller's existing workflows, runtime files, scripts, and branch
   rules. Decide which shared job it needs and which project-specific jobs it
   should keep.
2. Find the relevant file in [.github/workflows/](.github/workflows/) and confirm
   it exposes `workflow_call`. Choose a release or reviewed revision, resolve it
   to a full commit SHA, and read the workflow at that SHA. Current branch
   documentation may describe changes absent from the selected release.
3. Read its caller prerequisites, input and secret declarations, job conditions,
   permissions, and commands. Prepare the caller's required files and service
   settings. For an incompatible project layout, add a root wrapper or keep the
   job local.
4. Call it from a job's `uses:` field. Pin the full SHA with a version comment
   and set needed inputs under `with:`. The caller owns events, activity types,
   and branch filters. Grant the called jobs' required permissions and pass
   secrets by their declared names, without `secrets: inherit`. Restrict named
   tokens separately; job permissions only govern `GITHUB_TOKEN`. Keep ordinary
   PR CI read-only and free of secrets.
5. Run the caller's checks and lint its workflows. Exercise the intended event
   in GitHub Actions and confirm the observed check names before changing branch
   protection. Keep caller and called job names stable afterward.
6. For upgrades, compare the pinned and proposed workflow definitions and read
   the intervening release notes. Review executable changes, update caller
   configuration as needed, and repeat validation.

## Changing this repository

1. Read the affected workflow and its callers before editing. Keep reusable jobs
   small and application-specific logic in consumers. Preserve public input,
   secret, and check names unless the change includes a migration plan. Quality
   workflows keep a root verification script; do not add arbitrary command or
   directory inputs.
2. Keep workflow-specific setup and tradeoffs beside the code. Inputs, defaults,
   permissions, and validation rules belong in YAML. Comments should explain
   requirements the YAML cannot express. Markdown covers purpose and process;
   do not add parallel catalogs, permission tables, or copies of workflow rules.
3. Review workflow edits as executable code, including dependency updates. Pin
   third-party actions to full SHAs with version comments and verify each pin
   against its official upstream release tag. Keep permissions minimal and
   privileged jobs isolated from untrusted PR code.
4. Follow [policy.yml](.github/workflows/policy.yml) for validation commands and
   tool versions. Run `git diff --check` and `actionlint` from the root, validate
   changed YAML and JSON, use any configured formatter, and inspect the parsed
   YAML and final diff. Report checks you could not run. Repository CI should
   stay deterministic and validate this repository's workflows.
5. Use the title rules in
   [conventional-commit-title.yml](.github/workflows/conventional-commit-title.yml).
   Explain the resulting behavior, validation, and any caller migration in the
   PR. Mark breaking changes with `!`; before stable 1.x they use a 0.x minor
   release. Let [release.yml](.github/workflows/release.yml) and the root release
   metadata manage versions, tags, and the changelog.
