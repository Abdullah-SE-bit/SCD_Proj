# GitHub protection evidence (2026-11-28)

Captured from the GitHub API and `git push` output during Phase 0, in the order the operations ran.

## 1. main protected first
```
{"admins":true,"checks":21,"conv":true,"delete":false,"dismiss_stale":true,"force":false,"reviews":1,"strict":false}
{"allow_auto_merge":false,"allow_merge_commit":true,"allow_rebase_merge":false,"allow_squash_merge":false}
```

## 2. dev created from main and protected
```
dev -> 26b564257bbb497d332cf1eb0193b58fba0e4418
{"admins":true,"checks":21,"conv":true,"delete":false,"force":false,"reviews":0,"strict":true}
```

## 3. Negative probes (run as the repository administrator; all rejected)
```
direct push main  : GH006: Protected branch update failed for refs/heads/main
delete main       : [remote rejected] main (refusing to delete the current branch)
direct push dev   : GH006: Protected branch update failed for refs/heads/dev
delete dev        : GH006: Protected branch update failed for refs/heads/dev
force push main   : GH006: Protected branch update failed for refs/heads/main
afterwards        : main and dev both still at 26b5642
```

Not yet exercised: a merge blocked by a failing check, and a promotion blocked for lack of approval.
