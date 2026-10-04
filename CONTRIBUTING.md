# Contributing

Contribute reusable workflows, validation, or examples. Keep application builds,
deployment, publishing, and environment rules in the caller. Add a package
manager or security tool only when this repository needs it.

## Before opening a pull request

From the repository root:

```sh
git diff --check
actionlint
python3 -m json.tool release-please-config.json > /dev/null
python3 -m json.tool .release-please-manifest.json > /dev/null
```

Use `actionlint` v1.7.12 to match [repository CI](.github/workflows/policy.yml).
If it is unavailable, inspect each changed workflow and say so in the PR.
Validate changed YAML and JSON, use the configured formatter if there is one,
and inspect the parsed YAML and final diff.

Use a Conventional Commit title, such as `ci: validate workflow YAML` or
`docs(readme): clarify callers`. The [title check](README.md#conventional-commit-title)
lists supported types and enforces the 72-character limit and no final period.
Dependabot titles are exempt. PRs are squash-merged, so the title becomes the
commit subject.

## Workflow changes

- Use lowercase kebab-case filenames and distinct workflow display names.
  Keep job names stable because they determine required check names.
- Prefer kebab-case for new `workflow_call` inputs and uppercase names for new
  named secrets. Existing input and secret names are part of the public
  interface; do not rename them solely for style.
- Pin third-party actions to full commit SHAs with version comments. Before
  updating a pin, verify it against the official upstream tag and review the
  upstream changes.
- Grant only the permissions each job needs. Treat fork PRs as untrusted and
  keep secrets out of ordinary PR validation.
- Use the reusable Release Please workflow for releases. Keep
  `include-v-in-tag` and `include-v-in-release-name` set to `false`. Preserve
  historical `v` tags and the current manifest version when migrating. The next
  release creates a tag without `v`; do not delete or duplicate old tags.
- Keep release triggers and branch filters in each caller. Pass
  `target-branch: ${{ github.ref_name }}` for named release branches. The reusable
  workflow accepts only branch pushes and manual dispatches and defaults to the
  caller's branch.
- Preserve the [Dependabot auto-merge safeguards](README.md#dependabot-auto-merge).
  Use `pull_request`, verify both actor and author, and never check out PR code.
  Keep the fine-grained token in Dependabot secrets for compatibility lookups
  and auto-merge. GitHub Actions updates require manual review.
- Quality workflows accept no inputs and run only the caller's root `verify`
  script. Keep their required files documented in the workflow comments.
  For other layouts, use a root wrapper or keep the job in the caller. Do not
  add command or directory overrides. Runtime pins belong in the caller's
  `mise.toml`; a Bun pin here would not configure callers.
- Document inputs, defaults, required files, permissions, and security effects
  in the README. Check existing callers before changing an interface and include
  upgrade notes when callers need edits.
- Before 1.x, use `!` in the title for breaking changes and release them as a
  0.x minor. Compatible additions are minors; fixes are patches.
- Keep repository policy deterministic. It must validate all workflow YAML and
  call the local `conventional-commit-title.yml`, without application-specific CI.

See [AGENTS.md](AGENTS.md) for agent instructions and [SECURITY.md](SECURITY.md)
to report vulnerabilities.
