# workflows

Reusable GitHub Actions workflows for [Abijith Suresh](https://github.com/abijith-suresh)'s
repositories. Shared jobs cover quality checks, pull request checks, release
automation, Dependabot updates, and preview cleanup. Callers keep their triggers
and application-specific build, deployment, and publishing logic.

## Start here

Read [AGENTS.md](AGENTS.md) to adopt a workflow or change this repository. It is a
process guide for people and agents working in either repository.

The [workflow files](.github/workflows/) define the interfaces and behavior.
Their comments explain caller prerequisites that GitHub Actions cannot express
in `workflow_call`. Read the file at the revision you plan to use.

[Releases](https://github.com/abijith-suresh/workflows/releases) and the generated
[CHANGELOG.md](CHANGELOG.md) record published changes.

Report vulnerabilities through [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE).
