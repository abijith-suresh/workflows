# workflows

Reusable GitHub Actions workflows for [Abijith Suresh](https://github.com/abijith-suresh)'s
repositories. Callers keep their triggers and application-specific checks,
deployment, and publishing logic.

## Adopting a workflow

1. Inspect the caller's existing CI and choose a shared job from
   [.github/workflows/](.github/workflows/). Only files exposing `workflow_call`
   are reusable.
2. Choose a release or reviewed revision, resolve it to a full commit SHA, and
   read the workflow at that SHA. Its declarations, commands, and caller
   comments define what to configure; the current branch may differ.
3. Prepare the required files and service settings. Call the workflow from a
   job's `uses:` field with the full SHA and a version comment. Set needed inputs
   under `with:` and keep event and branch filters in the caller. For other
   project layouts, add a root wrapper or keep the job local.
4. Grant the called jobs' required permissions and pass only declared secrets
   by name. Scope named tokens separately; job permissions govern `GITHUB_TOKEN`.
   Keep ordinary PR CI read-only and free of secrets.
5. Run the caller's checks and lint its workflows. Exercise the intended Actions
   event and confirm check names before updating branch protection. On upgrades,
   review the workflow diff and release notes, then repeat validation.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for changes to this repository and
[SECURITY.md](SECURITY.md) to report vulnerabilities.

Published changes appear in [releases](https://github.com/abijith-suresh/workflows/releases)
and the generated [changelog](CHANGELOG.md).

[MIT license](LICENSE).
