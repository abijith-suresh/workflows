# AGENTS.md

## Purpose

This repository provides a small set of reusable GitHub Actions workflows for
Abijith Suresh's repositories. It is also a transparent learning and reference
project: examples should make the reasoning behind an Actions choice easy to
inspect.

## Workflow conventions

- Keep reusable interfaces under `.github/workflows/` and expose only the
  inputs that are part of a deliberate contract through `workflow_call`.
- The shared quality workflows are intentionally zero-input root contracts:
  npm callers provide root `.node-version`, `package-lock.json`, and
  `package.json` with exact `packageManager: npm@major.minor.patch`; Bun
  callers provide an exact root `.bun-version` in `major.minor.patch` form,
  root `bun.lock`, and root `package.json` with an exact
  `packageManager: bun@major.minor.patch` value equal to `.bun-version`. Both
  provide a root `verify` script. They run only `npm run verify` or
  `bun run verify` and must not accept arbitrary shell commands or directory
  overrides.
- If a project is exceptional, add a root compatibility wrapper that exposes
  this contract or keep package-specific quality logic in the consumer. Projects
  such as snapserve remain local until they provide that wrapper. Do not
  reintroduce generic `verify-command` or `working-directory` inputs.
- The Conventional Commit title workflow accepts the central type list
  (`build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`,
  `style`, `test`), limits the complete title to 72 characters, and rejects a
  subject ending in a period. Dependabot titles remain exempt.
- Give each workflow and job a clear, unique name. Keep validation focused on
  the behavior the repository actually owns.
- Default to least privilege. A called workflow cannot grant permissions that
  its caller did not grant, so document the minimum caller permissions.
- Pin every third-party action to a full commit SHA and retain a version comment.
  Review pin updates as executable infrastructure, not as cosmetic dependency
  changes. Verify each SHA against its official upstream release tag.

## Pull request and fork safety

Treat workflow files, workflow inputs, and commands run by reusable workflows as
executable code. For untrusted pull requests and forks, prefer `pull_request`
over `pull_request_target`, use read-only permissions, and do not expose
secrets. In particular, do not add `secrets: inherit` or privileged checkout
patterns without a specific, reviewed need.

## Validation

From the repository root, run `git diff --check` and `actionlint` (v1.7.12
when matching repository policy). Validate changed YAML and JSON, format files
when a formatter is configured, inspect the rendered YAML, and inspect the
final diff as well. Keep the repository's policy workflow deterministic and
free of application-specific CI. The quality workflows read runtime files
from the checked-out caller; this repository does not provide a central
`.bun-version` or other runtime file that controls callers. This repository is
not a Bun consumer, so adding `.bun-version` here would not affect callers.

## Releases and documentation

After review, reusable interface changes may be published with a versioned tag
or GitHub release. Consumers still pin the immutable commit SHA and keep the
release/version in a comment. Use a new major version for breaking interface
changes; document inputs, permissions, security effects, and upgrade notes in
the same change.

Keep README examples and contributor guidance concise and accurate. Prefer
small examples and recorded tradeoffs over generic policy prose. Changes should
help a reader learn how reusable workflows, permissions, pinning, and untrusted
code interact.
