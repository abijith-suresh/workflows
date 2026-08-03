# workflows

This repository has two purposes:

1. reusable GitHub Actions workflows for [Abijith Suresh](https://github.com/abijith-suresh)'s repositories; and
2. a small, transparent learning and reference project for designing safe,
   maintainable workflows.

It is intentionally not a general-purpose CI platform. Application-specific
build, deploy, release, publishing, and environment policy stay in the
consuming repository.

## Workflows

- [`bun-quality.yml`](.github/workflows/bun-quality.yml) installs a caller's
  root Bun dependencies and runs `bun run verify`.
- [`npm-quality.yml`](.github/workflows/npm-quality.yml) installs a caller's
  root npm dependencies and runs `npm run verify`.
- [`dependency-review.yml`](.github/workflows/dependency-review.yml) reviews
  dependency changes in a pull request without installing or running project
  code.
- [`pr-title.yml`](.github/workflows/pr-title.yml) checks a pull request title
  against the supported Conventional Commit format.
- [`policy.yml`](.github/workflows/policy.yml) is repository-local validation:
  it runs `actionlint` on the workflow YAML and calls `pr-title.yml` for pull
  requests. It does not provide application CI.

## Calling a reusable workflow

A caller owns the event trigger and delegates one job to this repository. Pin
that job to a full commit SHA; the version comment is a readable upgrade hint,
not the security boundary. The npm quality example below uses the immutable
commit being reviewed in this PR; after release, replace it with the immutable
commit for the released version and update its comment. The Bun workflow in this
PR uses the same pinned, zero-input pattern.

The quality workflows have deliberately strict, zero-input root contracts.
Before calling one, the consumer must put the runtime metadata, package
manifest, lockfile, and verification script at its repository root:

- npm projects must have a root `.node-version`, a root `package-lock.json`,
  and a root `package.json` whose `packageManager` is exactly
  `npm@major.minor.patch` (for example, `npm@10.9.2`).
- Bun projects must have an exact root `.bun-version`, a root `bun.lock`, and a
  root `package.json` whose exact `packageManager` value agrees with that Bun
  version (for example, `bun@1.2.3`).
- Both projects must define a root `verify` script. The workflows run only
  `npm run verify` or `bun run verify` and accept no command or directory
  overrides.

The Bun workflow requires the caller's root `.bun-version`; it never falls
back to `latest`. Its migration is a breaking change for callers of the old
input-based interface: remove `working-directory` and `verify-command`, move
or wrap the project so the required root files exist, and use the zero-input
job call.

```yaml
name: Quality

on:
  pull_request:

permissions:
  contents: read

jobs:
  npm-quality:
    uses: abijith-suresh/workflows/.github/workflows/npm-quality.yml@6136c325cd1618188affefe2be3a343953fa65af # PR commit; replace with released commit after merge
    permissions:
      contents: read

```

The npm job is a zero-input call: do not add `with`, `verify-command`, or
`working-directory`. This is a breaking upgrade for npm callers of the earlier
input-based interface: remove those inputs and add the required root metadata
before switching the workflow pin. The npm workflow checks out the caller,
reads Node from its root `.node-version`, reads and validates the root
`packageManager` after Node setup, installs that exact npm version, caches only
`package-lock.json` at the root, runs `npm ci`, and then runs `npm run verify`.
The Bun workflow checks out the caller, reads Bun from its exact root
`.bun-version`, runs `bun install --frozen-lockfile` and then `bun run verify` at
the root. Neither workflow uses secrets.

The quality workflows read runtime files from the checked-out caller repository.
The workflows repository does not provide a central `.bun-version` (or a
central runtime file that controls callers); this repository is not a Bun
consumer, and a file here would not affect callers. Maintainers should use
local runtime tooling when working on this repository.

The implementation follows GitHub's
[reusable workflow guidance](https://docs.github.com/en/actions/sharing-automations/reusing-workflows),
[`setup-node`'s version-file and cache inputs](https://github.com/actions/setup-node#readme),
[`setup-bun`'s version-file input](https://github.com/oven-sh/setup-bun#readme),
and npm's [package.json metadata documentation](https://docs.npmjs.com/cli/v11/configuring-npm/package-json).

```yaml
name: Pull request title

on:
  pull_request:

permissions:
  pull-requests: read

jobs:
  pr-title:
    uses: abijith-suresh/workflows/.github/workflows/pr-title.yml@b42be9571985efb1ce10970340250fcccc657050 # v0.1.0
    permissions:
      pull-requests: read
```

```yaml
name: Dependency review

on:
  pull_request:

permissions:
  contents: read

jobs:
  dependency-review:
    uses: abijith-suresh/workflows/.github/workflows/dependency-review.yml@b42be9571985efb1ce10970340250fcccc657050 # v0.1.0
    with:
      fail-on-severity: high
    permissions:
      contents: read
```

`dependency-review.yml` reviews dependency diffs through GitHub's dependency
graph; it does not install Bun or npm dependencies or run project scripts. Keep
quality and build workflows separate in the consuming repository.

Reusable workflows are jobs, not steps: a job using `uses` cannot also define
`runs-on` or `steps`. See GitHub's
[reusable workflow documentation](https://docs.github.com/en/actions/sharing-automations/reusing-workflows).

### Quality workflow inputs

Both quality workflows intentionally expose **no inputs**. Their interfaces
are root conventions rather than caller-supplied commands:

| Workflow | Required root contract |
| --- | --- |
| `npm-quality.yml` | `.node-version`, `package.json` with exact `packageManager: npm@major.minor.patch`, `package-lock.json`, and a `verify` script. |
| `bun-quality.yml` | Exact `.bun-version`, `package.json` with an agreeing exact `packageManager: bun@major.minor.patch`, `bun.lock`, and a `verify` script. |

The npm workflow parses `packageManager` as metadata, requires the complete
`npm@major.minor.patch` form with no range, alias, or prerelease, and installs
that exact npm version before `npm ci`. It operates at the caller's repository
root and does not evaluate arbitrary shell input.

The Bun workflow uses the documented `bun-version-file: .bun-version` input,
has no `latest` fallback, and runs the frozen install and verification script
at the caller's root. A Bun caller that cannot provide this root contract
should keep its quality workflow local. In particular, snapserve remains local
until it provides a root compatibility wrapper with the required Bun metadata,
lockfile, and `verify` script.

This contract favors the dominant repository layout over a generic monorepo
adapter. An exceptional project should add a root compatibility wrapper that
exposes the required `verify` script and root lockfile/runtime metadata, or
retain its package-specific quality workflow locally. Projects such as snapserve
remain local until they can provide that wrapper. Do not weaken the shared
workflow with directory or command inputs. Package-specific builds, Changesets,
matrices, smoke tests, deployment, and release logic remain in the caller.

### `dependency-review.yml` inputs

| Input | Required | Default | Purpose |
| --- | --- | --- | --- |
| `fail-on-severity` | No | `high` | Fails when a dependency diff introduces a vulnerability at or above this severity. |

The supported values are `low`, `moderate`, `high`, and `critical`.

### Permissions and security

- Grant only the permissions the called workflow needs: `contents: read` for
  `bun-quality.yml`, `npm-quality.yml`, and `dependency-review.yml`, or
  `pull-requests: read` for `pr-title.yml`. Dependency review does not post
  pull request comments. The quality workflows need no secrets.
- Use `pull_request`, not `pull_request_target`, when a workflow checks pull
  request code. Keep fork jobs read-only and do not pass secrets to them.
- These reusable workflows require no repository secrets. Do not use
  `secrets: inherit` unless a separately reviewed workflow genuinely needs it.
- All third-party actions in this repository are pinned to full commit SHAs.
  Review pin changes as executable CI changes.

## What stays local to callers

Consuming repositories choose their own triggers, application tests and build
matrices, deployments, environments and approvals, secrets, publishing, and
application-specific release automation. For outpost, its matrix, build,
smoke-test, and release jobs remain local to that repository. Branch protection
is a repository setting, and releases are tags/GitHub releases or release
workflows; neither is implicitly provided to consuming repositories by these
reusable workflows.

## Versioning and learning notes

Until a stable `1.x` line is intentionally declared, this project follows a
pre-1.0 maturity policy: release-worthy fixes and maintenance changes use
patch releases, while meaningful additions use minor releases. Breaking
interface changes before 1.0.0 remain in the 0.x line; use a new major version
only after a stable 1.x line has been declared. Callers should continue to pin
the full commit SHA and keep the release in a comment. Document input,
permission, and security changes alongside the implementation.

The repository's own GitHub Actions dependencies are checked weekly by
Dependabot. For contribution and security guidance, see
[CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and
[AGENTS.md](AGENTS.md).

## Automated releases

Release Please runs in manifest mode from `.github/workflows/release-please.yml`
on pushes to `main` (and manually through `workflow_dispatch`; it does not run
on pull requests). It opens or updates one release PR containing changes to
`CHANGELOG.md`, `VERSION`, and `.release-please-manifest.json`. After that
release PR is merged, Release Please creates the corresponding SemVer tag and
GitHub Release.

The mistaken `v1.0.0` tag was deleted. `v0.1.0` is the current released
baseline at commit `b42be9571985efb1ce10970340250fcccc657050`. Future workflow
changes should be consumed through the immutable commit for the release that
contains them; tags and GitHub Releases are created only by the release process
after a change is merged. The simple strategy is configured
to use `VERSION`, and component names are omitted so future tags continue to be
generated without a component prefix.

Before relying on releases, a maintainer must add a fine-grained token as the
repository Actions secret `RELEASE_PLEASE_TOKEN`. Do not commit a token or
create an empty placeholder. The token should be limited to this repository
with only the permissions Release Please needs: **Contents: read and write**,
**Issues: read and write**, and **Pull requests: read and write** (repository
metadata read is required automatically). No repository secret or setting is
managed by this repository. If repository policy requires it, a maintainer
must also allow GitHub Actions to create pull requests; that setting is
intentionally not changed here.

Use the existing pull-request title policy for changes that affect releases:

- `fix:` (including `fix(ci): ...`) produces a patch release for fixes and
  release-worthy maintenance.
- `feat:` (including `feat(ci): ...`) produces a minor release for meaningful
  additions.
- Before 1.0.0, any type with `!` or a `BREAKING CHANGE` footer uses Release
  Please's `bump-minor-pre-major` setting and stays in the 0.x line instead of
  creating a 1.0.0/major release.
- A workflow behavior change should use `feat(ci): ...` when it adds a
  capability, `fix(ci): ...` when correcting behavior, or the corresponding
  `!` form when it breaks a caller. Use `ci:` or `chore:` for non-release-
  worthy maintenance.

## License

MIT. See [LICENSE](LICENSE).
