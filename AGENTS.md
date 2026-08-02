# AGENTS.md

## Purpose

This repository provides a small set of reusable GitHub Actions workflows for
Abijith Suresh's repositories. It is also a transparent learning and reference
project: examples should make the reasoning behind an Actions choice easy to
inspect.

## Workflow conventions

- Keep reusable interfaces under `.github/workflows/` and expose inputs and
  permissions explicitly through `workflow_call`.
- Give each workflow and job a clear, unique name. Keep validation focused on
  the behavior the repository actually owns.
- Default to least privilege. A called workflow cannot grant permissions that
  its caller did not grant, so document the minimum caller permissions.
- Pin every third-party action to a full commit SHA and retain a version comment.
  Review pin updates as executable infrastructure, not as cosmetic dependency
  changes.

## Pull request and fork safety

Treat workflow files, workflow inputs, and commands run by reusable workflows as
executable code. For untrusted pull requests and forks, prefer `pull_request`
over `pull_request_target`, use read-only permissions, and do not expose
secrets. In particular, do not add `secrets: inherit` or privileged checkout
patterns without a specific, reviewed need.

## Validation

From the repository root, run `git diff --check` and `actionlint`. `actionlint`
should cover every YAML file in `.github/workflows/`; inspect the rendered YAML
and the final diff as well. Keep the repository's policy workflow deterministic
and free of application-specific CI.

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
