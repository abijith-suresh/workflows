# workflows

Reusable GitHub Actions workflows for [Abijith Suresh](https://github.com/abijith-suresh)'s repositories, and a small reference project for safe workflow design.

Not a general-purpose CI platform. Triggers, matrices, smoke tests, deployments, Changesets, and publishing stay in the consuming repository.

## Workflows

- [`bun-quality.yml`](.github/workflows/bun-quality.yml): install a caller's root Bun dependencies, run `bun run verify`.
- [`npm-quality.yml`](.github/workflows/npm-quality.yml): install a caller's root npm dependencies, run `npm run verify`.
- [`dependency-review.yml`](.github/workflows/dependency-review.yml): review dependency diffs without installing or running project code.
- [`conventional-commit-title.yml`](.github/workflows/conventional-commit-title.yml): check a PR title (types, 72 chars max, no trailing period; Dependabot exempt).
- [`release-please.yml`](.github/workflows/release-please.yml): reusable release automation (also drives this repository's own releases).
- [`policy.yml`](.github/workflows/policy.yml): repository-local validation (`actionlint`, `git diff --check`, release-metadata JSON, plus the title check on PRs).

The workflow files are the source of truth for their contracts. This README shows only how to call them.

## Calling a reusable workflow

A caller owns the trigger and delegates one job. Pin the job to a full commit SHA; the version comment is an upgrade hint, not the security boundary. Examples pin `v0.4.1` at `e59572c426373f5864ef1a6dad2524b47280a30c`.

### Quality (Bun and npm)

Both quality workflows are zero-input: no `with`, no command or directory overrides. The caller provides, at its repository root:

- Bun: `mise.toml` with exactly one `bun` version under `[tools]` plus `node`, a `bun.lock`, a `package.json`, and a `verify` script that is exactly:
  `bun run type-check && bun run lint && bun run format:check && bun run test && bun run build`
- npm: `mise.toml` with exactly one `node` and one `npm` version under `[tools]`, a `package-lock.json`, a `package.json`, and a `verify` script that is exactly:
  `npm run format:check && npm run lint && npm run typecheck && npm run test && npm run build`

No extra steps in `verify`; fold custom checks into the matching standard script. Current fleet standards: `bun = "1.4.1"`, `node = "24.20.0"`, `npm = "11.16.0"`. Versions moved from `.node-version`/`.bun-version`/`packageManager` into `mise.toml`, which is now the only version source.

```yaml
name: Quality

on:
  pull_request:

permissions:
  contents: read

jobs:
  npm-quality:
    uses: abijith-suresh/workflows/.github/workflows/npm-quality.yml@e59572c426373f5864ef1a6dad2524b47280a30c # v0.4.1
    permissions:
      contents: read

  bun-quality:
    uses: abijith-suresh/workflows/.github/workflows/bun-quality.yml@e59572c426373f5864ef1a6dad2524b47280a30c # v0.4.1
    permissions:
      contents: read
```

A project that cannot provide this root contract keeps its quality workflow local (`t3code`, `snapserve`) or adds a root compatibility wrapper exposing the required files.

### Title, dependency review, releases

```yaml
jobs:
  pr-title:
    uses: abijith-suresh/workflows/.github/workflows/conventional-commit-title.yml@e59572c426373f5864ef1a6dad2524b47280a30c # v0.4.1
    permissions:
      pull-requests: read

  dependency-review:
    uses: abijith-suresh/workflows/.github/workflows/dependency-review.yml@e59572c426373f5864ef1a6dad2524b47280a30c # v0.4.1
    with:
      fail-on-severity: high # low | moderate | high | critical
    permissions:
      contents: read

  release-please:
    uses: abijith-suresh/workflows/.github/workflows/release-please.yml@e59572c426373f5864ef1a6dad2524b47280a30c # v0.4.1
    permissions:
      contents: write
      issues: write
      pull-requests: write
    secrets:
      RELEASE_PLEASE_TOKEN: ${{ secrets.RELEASE_PLEASE_TOKEN }}
```

Release callers keep only `release-please-config.json` (single package, `bump-minor-pre-major: true`, `include-component-in-tag: false`, `include-v-in-tag: false`) and `.release-please-manifest.json` at their root, plus a fine-grained `RELEASE_PLEASE_TOKEN` (Contents/Issues/Pull requests: read and write). Tags have no `v` prefix. `outpost` and `planview` stay on Changesets instead. Never use `secrets: inherit`.

## Permissions and security

Grant only what the called workflow needs (`contents: read` for quality/dependency-review, `pull-requests: read` for title, writes only for release-please). Use `pull_request`, not `pull_request_target`; keep fork jobs read-only with no secrets. All third-party actions are pinned to full SHAs; review pin updates as executable changes.

## Check names & branch protection

Checks display as `<caller job> / <called job>`. Keep both halves stable:

| Caller job | Called workflow | Required check |
| --- | --- | --- |
| `pr-title` | `conventional-commit-title.yml` | `pr-title / Validate title` |
| `bun-quality` | `bun-quality.yml` | `bun-quality / Install and verify` |
| `npm-quality` | `npm-quality.yml` | `npm-quality / Install and verify` |
| `dependency-review` | `dependency-review.yml` | `dependency-review / Review dependency changes` |

## Versioning and releases

Pre-1.0 policy: fixes ship as patches, additions as minors, and breaking changes stay in the 0.x line via `!` (a new major only after 1.x is declared). Consume changes through the immutable commit of their release.

Release Please opens one release PR (`CHANGELOG.md`, `VERSION`, manifest); merging it creates the tag and GitHub Release. Title policy drives versions: `fix:` patch, `feat:` minor, `!` minor pre-1.0, `ci:`/`chore:` non-release maintenance.

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [AGENTS.md](AGENTS.md).

## License

MIT. See [LICENSE](LICENSE).
