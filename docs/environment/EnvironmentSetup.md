# Environment setup

Required: Git, GitHub CLI logged in for your account, Python 3.12+, uv (or pip), Node 24, Docker, kubectl,
kind, Claude Code.

1. Clone into the folder named for you (`SCD_Proj` or `SCD_Proj_demidoga`).
2. Set local `user.name`, `user.email` and the pinned credential helper (replace LOGIN):
```bash
git config --local --add credential.https://github.com.helper ""
git config --local --add credential.https://github.com.helper '!f() { test "$1" = get || exit 0; t=$(gh auth token --hostname github.com --user LOGIN) || exit 1; echo username=LOGIN; echo password=$t; }; f'
```
3. Put the two PDFs into `docs/source/`.
4. Verify:
```bash
python harness/verification/scd.py identity
uv run --no-project --python 3.12 --with-requirements requirements-dev.txt python harness/verification/scd.py all
```
`k8s-validate` needs `kubeconform` on PATH. Application setup does not exist yet.
