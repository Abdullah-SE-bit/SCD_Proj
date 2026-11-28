Title: Services use the Python standard library

Status: Applied in P01; awaiting human review.

Context: `docs/research/TechStack.md` proposed FastAPI, Pydantic and httpx. CI installs only `requirements-dev.txt`,
a protected file that lists test and lint tools, so framework code could not be tested or type-checked in CI. Changing
protected files needs maintenance mode, which only the owner can enable; it was not enabled.

Options: (1) enable maintenance mode and add the frameworks to CI; (2) use the standard library (`http.server`,
`urllib`) with a small shared base; (3) keep FastAPI and skip those tests in CI.

Decision: Option 2. Each module carries an identical copy of `base.py`; a test keeps the copies identical. A library
needed only at run time goes in the module's `requirements.txt`, is imported where it is used and is faked in tests.

Why: Every check runs on real code with no skipped tests (option 3 was rejected for that reason). Images stay small.

Cost: No automatic request validation or OpenAPI generation; the base is duplicated; module requirements are not
audited by the dependency check; `ThreadingHTTPServer` is not built for high load, which the load test in P10.01 may
show.

AI use: Context, options and text drafted by Claude, which also made the choice while implementing P01.02.
