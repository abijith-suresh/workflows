# Adopting browser tests

[browser-tests.yml](../.github/workflows/browser-tests.yml) installs the caller's
locked dependencies and Playwright browsers, then runs its root browser-test
script. Its inputs and caller prerequisites are defined in the YAML. Test cases,
build commands, preview servers, project selection, retries, and diagnostic
settings belong in the consuming repository.

Follow the [adoption process](../README.md#adopting-a-workflow) and the caller's
repository instructions. A browser subset only changes which engines are
installed. Match the caller's configured projects to that subset, or keep all
three engines for full coverage.

## abijith.sh migration

[abijith.sh PR #317](https://github.com/abijith-suresh/abijith.sh/pull/317),
squash-merged at `281457628efc7e16baf6780c3f692c0cc1bd3fdc`, added an inline
`browser-tests` job. Its root `test:browser` script builds Astro and runs
Playwright. Its config starts the preview server and runs Chromium, Firefox,
and WebKit. Keep that script, config, lockfile, runtime pins, and test cases in
abijith.sh.

After reviewing a shared-workflow revision, replace `FULL_COMMIT_SHA` below with
its full commit SHA and describe that revision in the comment. This job replaces
the inline job in `.github/workflows/ci.yml`:

```yaml
  browser-tests:
    name: Browser regressions
    uses: abijith-suresh/workflows/.github/workflows/browser-tests.yml@FULL_COMMIT_SHA # reviewed revision
    permissions:
      contents: read
    with:
      package-manager: bun
```

The existing root mise.toml already pins both Bun and Node. The shared job reads
both pins, replacing the inline mise-action setup. Preserve the caller's
pull-request branch filter, concurrency, Bun quality job, and dependency review
job. Keep all three browsers installed for this suite.

To migrate without a coverage gap:

1. Keep the inline job while adding a temporary `browser-tests-shared` job using
   the reviewed SHA. Give it a distinct name, such as `Browser regressions shared`.
   Open an adoption PR in abijith.sh and run both jobs on the same revision.
2. Confirm the shared job builds the site, starts the preview server, and runs
   the existing cases across all three engines. At the source revision, the
   expected result is 23 passes and one Firefox mobile-emulation skip. Review
   any changes to the suite since that revision before comparing counts.
3. Inspect the actual shared-job check name in Actions. Reusable workflows add
   a called-job component to check names, so preserving the caller job ID and
   display name alone does not preserve the original required check. If branch
   protection requires the inline check, add the observed shared check as a
   requirement before removing the old requirement and inline job.
4. Replace the inline job with the shared call above and remove the temporary
   call in the same adoption PR. Run the final PR revision and confirm all
   browser projects still pass before merging. Keep the inline job until the
   reviewed shared revision exists and has passed the canary run.

The source config already uses `trace: "retain-on-failure"`, so failures can
produce traces in `test-results/`. To include an HTML report, configure Playwright
in abijith.sh to use its HTML reporter alongside the existing console reporter,
with output in `playwright-report/` and automatic opening disabled in CI. Keep
custom diagnostic output in those directories if it should be uploaded. In the
adoption PR, temporarily force a browser assertion to fail, confirm the job
fails and its artifact contains a readable trace or report, then revert that
assertion and rerun. A killed or cancelled job may not finish writing diagnostics.

## npm callers

Use the same job call with `package-manager: npm` and prepare the caller according
to the YAML's root-file conventions. Its `test:browser` script owns any build
and invokes the locally installed Playwright runner. For a Chromium-only suite,
set `browsers: chromium` and configure the caller to run only Chromium projects.
Give each call a distinct `artifact-name` when several browser jobs share one
workflow run.

## Validation in this repository

Policy CI runs actionlint and
[browser workflow contract tests](../.github/tests/test_browser_workflow.py).
These execute the YAML's shell steps against temporary callers to check input
rejection, runtime pins, locked installs, browser arguments, and failure status
propagation. They also check setup conditions and the failure-artifact contract.
They do not launch browsers or exercise GitHub's reusable-workflow scheduling
and artifact service; the caller canary covers those behaviors.
