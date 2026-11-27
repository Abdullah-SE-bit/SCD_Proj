Title: Task branches into dev, promotion into protected main

Status: Accepted

Context: Two contributors work in parallel with AI sessions; the course requires protected main, pull requests,
required checks and review by the other member.

Options: (1) feature branches straight into main; (2) task branches into dev, then a promotion PR into main.

Decision: Option 2, as instructed by the project owner.

Why: Integration happens on dev with the same checks; main only receives reviewed, integrated states.

Cost: One extra pull request per promotion; task PRs into dev need no approval unless D-11 changes that, so peer
review there is policy rather than enforced.

AI use: Drafted by Claude from the owner's instruction; awaiting human review.
