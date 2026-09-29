# Portfolio rollout toward 1.0

Audit snapshot: 2026-09-24. The scope is the public repositories under the
`abijith-suresh` account. A project is ready for a shared quality workflow when
its root has a lockfile for one supported package manager, exact runtime
versions in `mise.toml`, and a root `verify` script.

## Projects and prerequisites

### Ready for the root contract

These Bun projects already have `bun.lock`, exact Bun in root `mise.toml`, and
root `verify`:

- `abijith.sh`
- `interleaf`
- `microbreak`
- `prompts`
- `skills`
- `tailory`
- `unwrapped`

### Add exact runtime versions first

These projects have the root lockfile and `verify` entry point, but need a root
`mise.toml` before they can call a shared quality workflow:

| Project | Package manager | Required root tool entries |
| --- | --- | --- |
| `agentic-astro` | Bun | exact `bun` version |
| `note-app` | Bun | exact `bun` version |
| `reshrimp` | Bun | exact `bun` version |
| `todo-app` | Bun | exact `bun` version |
| `wallpapers` | Bun | exact `bun` version |
| `outpost` | npm | exact `node` and `npm` versions |
| `planview` | npm | exact `node` and `npm` versions |

For Bun, use a root `bun.lock`; for npm, use a root `package-lock.json`. Both
contracts require a root `package.json` with a `verify` script. Keep runtime
versions exact (`major.minor.patch`) and declare each required tool once under
`[tools]` in `mise.toml`.

### Keep application-specific checks local

- `t3code` has a pnpm monorepo pipeline with workspace-specific checks.
- `snapserve` combines Java and Bun projects and does not expose one root
  quality contract.
- `receipts` needs root package metadata and a `verify` script before it can
  adopt the shared package workflow.
- Interleaf's QPDF/WASM and browser-fidelity checks remain local because they
  are specific to that application.
- `outpost` keeps Changesets, smoke checks, and publishing locally; `planview`
  keeps its app-specific preview and release logic locally.

Do not add a pnpm workflow just for `t3code`. Reconsider it if multiple smaller
projects converge on a pnpm root contract.

## Release tags

The shared Release Please contract uses tags without a `v` prefix. Historical
`v` tags stay in place; after migration, the next version becomes a no-`v` tag.
Keep each manifest at its current version and do not create a duplicate tag.

Current Release Please config snapshot:

| Already configured for no-`v` tags | Must set both no-`v` options before migration |
| --- | --- |
| `interleaf`, `tailory`, `unwrapped`, `workflows` | `agentic-astro`, `microbreak`, `note-app`, `reshrimp`, `todo-app` |

`note-app` and `todo-app` currently explicitly request `v` tags. The other
projects in the right column rely on Release Please's default `v` prefix.
Projects without a Release Please config can adopt the shared release workflow
only if they choose Release Please for their own release process.

`tailory` currently pins the shared release workflow to `v0.4.1`, which predates
the `workflow_call` interface. Update it to a released SHA containing the
reusable contract during its first migration PR.

`prompts` declares Bun 1.4.1 in `mise.toml` but 1.3.14 in `.bun-version`.
Reconcile or remove the duplicate version file when migrating so local tooling
and CI agree.

## Proposed PR and merge order

Keep the workflow library and consumer migrations reviewable. Each consumer PR
pins a released full SHA and updates that repository's required check names
when they change.

1. Publish the current 0.5.0 Release Please PR, then merge this shared-contract
   PR and publish its compatible 0.x release. That gives every consumer a
   released immutable SHA to pin.
2. Pilot in `tailory`, `interleaf`, and `unwrapped`. Tailory needs the corrected
   reusable Release Please pin; Interleaf exercises the Bun workflow while
   keeping its QPDF checks local; Unwrapped is another no-`v` Bun consumer.
3. Add `mise.toml` to `outpost` and adopt npm quality there as the npm pilot.
   Keep its Changesets, smoke checks, and publishing workflows local. Use the
   `patch-minor` Dependabot policy for this project.
4. Migrate the remaining ready Bun projects: `abijith.sh`, `microbreak`,
   `prompts`, and `skills`.
5. Add exact `mise.toml` entries and migrate the remaining Bun projects:
   `agentic-astro`, `note-app`, `reshrimp`, `todo-app`, and `wallpapers`.
6. Add exact Node and npm versions to `planview`, then migrate its quality
   workflow. Preserve its local release and preview behavior.
7. Move all adopted Release Please configs to the no-`v` policy, update callers
   to the shared workflow, and retain all historic tags. Keep project-specific
   title, dependency, deploy, and publish steps where they add value.
8. Declare 1.0 only after all 14 projects that meet or can meet the root
   contract use the documented contract or have a specific, recorded reason
   to stay local. At that point, freeze the interfaces, confirm permissions and
   required checks, and publish the stable contract release.

The order is a recommendation, not a batch rewrite. Finish and review each
consumer PR before starting the next one so CI failures can be attributed to a
single repository.

## Migration checks

For each consumer PR:

- Update one `Quality` caller job to the appropriate Bun or npm reusable
  workflow; do not pass commands or directory overrides.
- Keep repo-specific smoke, browser, deployment, Changesets, and publishing
  workflows in the consumer.
- Add caller permissions explicitly and pin the shared workflow to an immutable
  commit SHA with the release version in a comment.
- If adopting Dependabot auto-merge, map that repository's existing fine-grained
  token from Dependabot secrets to `DEPENDABOT_AUTOMERGE_TOKEN`. Limit the token
  to the repository and the required write permissions. The metadata action
  uses it for compatibility-score lookups; GitHub Actions updates stay manual.
  Do not expose the token to ordinary pull-request CI.
- Preserve historical release tags, keep the current manifest version, and
  check that the next Release Please tag has no `v` prefix.
- Update branch protection to the new stable check names after the reusable
  jobs have run successfully.
