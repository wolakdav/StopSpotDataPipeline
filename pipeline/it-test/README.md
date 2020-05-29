# Integration Testing

Integration testing is at present, a skeleton. In order to use the integration tests,
a database must be setup separate from all workspaces. The tests that currently exist
exercise the credentials systems, and how they function carried through the various
modules.

Credentials must be filled in, in a secure manner, within the empty fields inside
`test_integration.py` and the config assets within this directory.

When a proper testing environment is established, integration tests will create
testing input and output tables, environment variables, and spoof user interactive
input.

"GitHub Secrets" may be one possible for storing credentials safely for a testing
environment.