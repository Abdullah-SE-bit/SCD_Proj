# Failure recovery

| Failure | Action |
|---|---|
| Check fails | read the log, find the cause, fix on the task branch; never weaken the check |
| Hook blocks a legitimate action | stop; show the user the message; harness change needs authorisation |
| Hook script crashes | edits and commands are blocked; fix Python or ask the human to disable hooks in their UI |
| Claim left behind | the owner confirms, a human deletes `claim/<ID>` |
| Session lost or context cleared | resume from handoff, open PR and `git status` |
| Branch conflicts | merge `origin/dev` into the task branch, resolve, rerun checks |
| Wrong identity commit (unpushed) | fix identity, amend the author before pushing |
| Secret pushed | revoke immediately, tell the user, then rewrite only with human approval |
| Bad release | `kubectl rollout undo`; open a fix task |
| Other session silent | post on the PR; continue independent tasks; never act in its identity |
