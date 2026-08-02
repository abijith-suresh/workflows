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
```

`actionlint` validates the workflow YAML under `.github/workflows/`. If it is
not installed locally, inspect every changed workflow carefully and report that
limitation in the pull request. Keep changes focused, and review the final
diff rather than relying only on a formatter or generated output.

Pull request titles use Conventional Commits. Use one of the supported types
(`build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`,
`style`, or `test`), followed by an optional scope and `: ` plus a description;
for example, `ci: validate workflow YAML` or `docs(readme): clarify callers`.
Dependabot titles are exempt from this check. Changes are squash-merged after
review, so the pull request title should also make a good commit subject.

## Workflow changes

- Pin every third-party action to its full commit SHA and keep the human-readable
  version as a comment. Review the upstream change before updating a pin.
- Keep permissions at the narrowest useful scope. Do not add secrets to make a
  validation job convenient, and treat fork pull requests as untrusted.
- For a reusable workflow interface, describe the input, default, permission,
  and security implications in the README. Check existing callers before
  renaming an input, changing a default, or changing required permissions.
- Treat breaking interface changes as a new major version line. Keep compatible
  additions and behavior fixes on the existing line, and include upgrade notes
  when consumers must change their caller.
- If a change affects the repository's own validation, ensure the policy
  workflow still validates all workflow YAML and still exercises the local
  pull-request-title workflow.

See [AGENTS.md](AGENTS.md) for the repository conventions and
[SECURITY.md](SECURITY.md) for reporting workflow security issues.
