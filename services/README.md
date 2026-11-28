# Services

One directory per module. Each has its own package `scd_<name>`, Dockerfile and its image rules are tested in `tests/unit/`.

## Pattern (copy it for a new module)
- `scd_<name>/app.py` creates `service = Service("<name>", "<module>")`; run with `python -m scd_<name>.app`.
- `scd_<name>/base.py` is an identical copy in every service; `tests/unit/test_services.py` enforces that.
- `Dockerfile` (multi-stage, base pinned by digest, user 10001), `.dockerignore`, `requirements.txt` with `==` pins.
- The image builds with the module directory as context.

## Decision: Python standard library
`docs/research/TechStack.md` proposed FastAPI. CI installs only `requirements-dev.txt`, which is protected, so
services use the standard library (`http.server`, `urllib`, `jsonschema` already in CI for tests). A library needed
only at run time goes in the module's `requirements.txt`, is imported where it is used and is faked in unit tests.
Cost: no automatic request validation or OpenAPI generation, and module requirements are not audited by CI.
