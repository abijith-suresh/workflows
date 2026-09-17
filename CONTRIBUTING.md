# Contributing

This repository is for small, reusable GitHub Actions workflows and clear
learning material around them. A contribution should improve that shared
infrastructure or its documentation.

## Scope and non-goals

In scope are reusable workflow behavior, workflow interfaces, validation, and
examples. Application-specific build, deploy, release, publishing, and
environment policy remain in consuming repositories. Do not add a package
manager, broad application CI, or a security tool without a concrete need.

## Before opening a pull request

From the repository root:

```sh
git diff --check
actionlint
python3 -m json.tool release-please-config.json > /dev/null
python3 -m json.tool .release-please-manifest.json > /dev/null
```

`actionlint` validates the workflow YAML under `.github/workflows/`. If it is
not installed locally, inspect every changed workflow carefully and report that
limitation in the pull request. Keep changes focused, and review the final
diff rather than relying only on a formatter or generated output.

Pull request titles use Conventional Commits. Use one of the supported types
(`build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`,
`style`, or `test`), followed by an optional scope and `: ` plus a description;
for example, `ci: validate workflow YAML` or `docs(readme): clarify callers`.
The complete title must be at most 72 characters, and its subject must not end
with a period. Dependabot titles are exempt from this check. Changes are
squash-merged after review, so the pull request title should also make a good
commit subject.

## Workflow changes

- Pin every third-party action to its full commit SHA and keep the human-readable
  version as a comment. Verify the SHA against the official upstream tag and
  review the upstream change before updating a pin.
- Keep permissions at the narrowest useful scope. Do not add secrets to make a
  validation job convenient, and treat fork pull requests as untrusted.
- Use the reusable Release Please workflow for releases. Keep
  `include-v-in-tag` and `include-v-in-release-name` set to `false`; preserve
  historical `v` tags and establish a no-`v` baseline before the first
  migrated release.
- The shared quality workflows are zero-input root contracts (see AGENTS.md and
  the workflow files, which are the source of truth). Do not add
  consumer-specific logic or weaken the shared contract.
- If an exceptional project does not fit the root contract, add a root
  compatibility wrapper that exposes the required metadata and `verify` script,
  or retain package-specific workflow logic in that consumer. Projects such as
  snapserve remain local until they provide that wrapper. Do not add
  consumer-specific logic or weaken the shared contract.
- For a reusable workflow interface, describe the input, default, permission,
  and security implications in the README. A zero-input interface still needs
  its required root files and metadata documented. Check existing callers
  before renaming an input, changing a default, or changing required
  permissions.
- Treat breaking interface changes as a minor release before 1.x (title with
  `!`). Keep compatible additions and behavior fixes on the existing line, and
  include upgrade notes when consumers must change their caller.
- If a change affects the repository's own validation, ensure the policy
  workflow still validates all workflow YAML and still exercises the local
  `conventional-commit-title.yml` workflow.

See [AGENTS.md](AGENTS.md) for the repository conventions,
[SECURITY.md](SECURITY.md) for reporting workflow security issues, and the
[workflow README](README.md#calling-a-reusable-workflow) for the complete root
contract. The quality workflows read the caller's required root runtime files; this
repository does not provide a central `mise.toml` or other runtime file that
controls callers. It is not a Bun consumer, so do not add a Bun version pin here:
a file in this repository would not affect consuming repositories.
