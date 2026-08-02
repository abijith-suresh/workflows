# Security

The files in `.github/workflows/` are executable CI infrastructure. A change
can alter what code runs, which tokens are available, and whether untrusted pull
requests can reach secrets. Review workflow changes with the same care as
application code.

To report a suspected vulnerability, use GitHub's **Private vulnerability
reporting** entry in this repository's Security tab when it is enabled. If that
option is unavailable, use the security contact listed by the repository or
owner on GitHub. Do not open a public issue or include exploit details in a
public pull request.

Please include the affected workflow, a concise impact description, and safe
reproduction details. Do not submit credentials, tokens, or other secrets.
