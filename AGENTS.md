# AGENTS.md

## Purpose

This repository contains reusable GitHub Actions workflows for Abijith Suresh's
repositories. Explain workflow choices in comments and examples so readers can
learn from them.

## Workflow conventions

- Keep reusable workflows under `.github/workflows/`. Expose only inputs that
  callers need through `workflow_call`.
- Quality workflows accept no inputs and run only the root `verify` script in
  the caller's `package.json`. Their workflow comments define required files.
  Do not accept arbitrary shell commands or directory overrides.
  Bun callers need root `bun.lock`, `package.json`, and `mise.toml` files, with
  exactly one `bun` version under `[tools]`, such as `bun = "1.4.1"`.
  npm callers need root `package-lock.json`, `package.json`, and `mise.toml`
  files, with exactly one `node` and one `npm` version under `[tools]`, such as
  `node = "24.20.0"` and `npm = "11.16.0"`.
- For other project layouts, add a root wrapper with the required files and
  script, or keep package-specific quality logic in the caller. Do not
  reintroduce generic `verify-command` or `working-directory` inputs.
- The Conventional Commit title workflow accepts the central type list
  (`build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`,
  `style`, `test`), limits the complete title to 72 characters, and rejects a
  subject ending in a period. Dependabot titles remain exempt.
- Give workflows unique display names and jobs clear names. Choose caller job
  IDs that produce distinct, stable check names with the called job name.
  Validate behavior this repository controls.
- Grant only required permissions and document the caller's minimum. A called
  workflow cannot increase its caller's permissions.
- Use the reusable Release Please workflow to run releases. Callers provide
  package metadata and a token, set both
  `include-v-in-tag` and `include-v-in-release-name` to `false`, and own their
  trigger and release branch filters. They may pass `target-branch`, usually
  `${{ github.ref_name }}`. The reusable workflow defaults to the caller's
  branch and must not hardcode `main`. The reusable workflow runs only for
  branch `push` and `workflow_dispatch` events.
- Pin every third-party action to a full commit SHA and retain a version comment.
  Review upstream changes before updating a pin and verify each SHA against its
  official release tag.

## Pull request and fork safety

Treat workflow files, inputs, and commands as executable code. For untrusted PRs
and forks, prefer `pull_request` over `pull_request_target`, use read-only
`GITHUB_TOKEN` permissions, and keep secrets out of ordinary PR CI. Add
`secrets: inherit` or privileged checkout only for a specific, reviewed need.

- The reusable Dependabot auto-merge workflow is called from `pull_request` and
  never checks out or executes pull-request code. Dependabot-triggered
  `GITHUB_TOKEN`s are read-only, so callers pass a fine-grained token stored as
  a Dependabot secret. Keep it scoped to the target repository with only the
  write permissions required for pull-request auto-merge. The workflow checks
  both the event actor and PR author, uses the fine-grained token for the
  compatibility-score lookup and auto-merge request, and leaves GitHub Actions
  updates for manual review. Never call it from `pull_request_target` or expose
  that token to ordinary pull-request jobs.

## Validation

Run `git diff --check` and `actionlint` from the root. Use actionlint v1.7.12 to
match repository policy. Validate changed YAML and JSON, use the configured
formatter if there is one, and inspect the parsed YAML and final diff. Keep
repository policy deterministic and free of application-specific CI.

Quality workflows read the checked-out caller's runtime files. A `mise.toml`
here would not configure callers. This repository is not a Bun consumer and
does not need a Bun pin.

## Releases and documentation

After review, interface changes can be published with a versioned tag or release.
Consumers pin the commit SHA with a version comment. Before stable 1.x, breaking
changes use a 0.x minor release with `!` in the title. Use a new major only after
1.x. Document inputs, permissions, security effects, and upgrade notes with the
change.

Keep README examples and contributor guidance concise and accurate. Explain choices
about reusable workflows, permissions, pins, and untrusted code.
