"""Negative tests: each forbidden action must be detected. Everything runs in temporary repositories."""
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("scd", ROOT / "harness/verification/scd.py")
assert spec and spec.loader
scd = importlib.util.module_from_spec(spec)
sys.modules["scd"] = scd
spec.loader.exec_module(scd)

EMAIL = "tester@example.com"
OURS = "https://github.com/Abdullah-SE-bit/SCD_Proj/"
GH = "python harness/verification/scd.py gh -- "
# Assembled at run time so the repository scan does not flag this file.
FAKE_TOKEN = "gh" + "p_" + "A1b2" * 9


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def force_remove(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, onerror=force_remove)
        self.remote = self.tmp / "Abdullah-SE-bit" / "SCD_Proj.git"
        sh(self.tmp, "git", "init", "-q", "--bare", "-b", "main", str(self.remote))
        self.repo = self.tmp / "work" / "SCD_Proj"
        self.repo.mkdir(parents=True)
        for part in ("harness", "contracts", "config"):
            shutil.copytree(ROOT / part, self.repo / part, ignore=shutil.ignore_patterns("__pycache__"))
        (self.repo / "docs/requirements").mkdir(parents=True)
        (self.repo / "docs/source").mkdir(parents=True)
        shutil.copy(ROOT / scd.REQS_PATH, self.repo / scd.REQS_PATH)
        for path in (self.repo / scd.STATUS_DIR).glob("*.json"):
            path.unlink()
        self.policy = self.read(scd.POLICY_PATH)
        for who in self.policy["identities"].values():
            who["email_sha256"] = "0" * 64
        for role, name in (("secondary", "SCD_Proj"),):
            self.policy["identities"][role].update(
                email_sha256=hashlib.sha256(EMAIL.encode()).hexdigest(), git_name="Tester", clone_dir=name)
        self.write(scd.POLICY_PATH, self.policy)
        (self.repo / self.policy["source_checksums"]).write_text("")
        self.setup_clone(self.repo)
        sh(self.repo, "git", "init", "-q", "-b", "main")
        self.configure(self.repo)
        sh(self.repo, "git", "add", "-A")
        sh(self.repo, "git", "commit", "-qm", "base")
        sh(self.repo, "git", "remote", "add", "origin", self.remote.as_posix())
        sh(self.repo, "git", "push", "-q", "origin", "main", "main:dev")
        sh(self.repo, "git", "fetch", "-q", "origin")

    def setup_clone(self, path):
        path.mkdir(parents=True, exist_ok=True)

    def configure(self, repo, email=EMAIL):
        sh(repo, "git", "config", "user.name", "Tester")
        sh(repo, "git", "config", "user.email", email)
        sh(repo, "git", "config", "commit.gpgsign", "false")
        # same shape as the helper documented in docs/environment/EnvironmentSetup.md
        sh(repo, "git", "config", "--add", "credential.https://github.com.helper",
           '!f() { t=$(gh auth token --hostname github.com --user Demidoga) || exit 1; echo password=$t; }; f')

    def read(self, rel):
        return json.loads((self.repo / rel).read_text(encoding="utf-8"))

    def write(self, rel, data):
        target = self.repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data), encoding="utf-8")

    def done(self, *ids, status="done"):
        tasks = scd.tasks_by_id(self.repo)
        for tid in ids:
            reviewer = self.policy["identities"][tasks[tid]["reviewer"]]["login"]
            self.write(f"{scd.STATUS_DIR}/{tid}.json",
                       {"status": status, "pr": OURS + "pull/1", "evidence": [OURS + "pull/1"],
                        "reviewed_by": reviewer, "review": OURS + "pull/1#review"})

    def publish_dev(self, message="state"):
        sh(self.repo, "git", "add", "-A")
        sh(self.repo, "git", "commit", "-qm", message)
        sh(self.repo, "git", "push", "-q", "origin", "HEAD:dev")
        sh(self.repo, "git", "fetch", "-q", "origin")

    def branch(self, name):
        sh(self.repo, "git", "switch", "-qc", name)

    def decide(self, tool, **data):
        return scd.hook_decision(self.repo, {"tool_name": tool, "tool_input": data})[0]


class Identity(Fixture):
    def test_correct_identity_passes(self):
        self.assertEqual(scd.identity_problems(self.repo, self.policy), ("secondary", []))

    def test_wrong_contributor_detected(self):
        sh(self.repo, "git", "config", "user.email", "someone@else.test")
        self.assertIsNone(scd.identity_problems(self.repo, self.policy)[0])
        self.branch("feat/P01.01-x")
        self.assertEqual(self.decide("Bash", command="git commit -m x"), "deny")

    def test_wrong_credential_helper_detected(self):
        sh(self.repo, "git", "config", "--replace-all", "credential.https://github.com.helper", "manager")
        self.assertIn("credential helper", scd.identity_problems(self.repo, self.policy)[1][0])

    def test_wrong_repository_detected(self):
        sh(self.repo, "git", "remote", "set-url", "origin", "https://github.com/other/Project.git")
        self.assertIn("wrong repository", scd.identity_problems(self.repo, self.policy)[1][0])


class Commands(Fixture):
    def test_direct_commit_on_protected_branches(self):
        self.assertEqual(self.decide("Bash", command="git commit -m x"), "deny")
        self.branch("dev")
        self.assertEqual(self.decide("PowerShell", command="git commit -m x"), "deny")

    def test_dangerous_commands_denied(self):
        self.branch("feat/P01.01-x")
        for line in ["git push origin main", "git push origin HEAD:dev", "git push -u origin dev",
                     "git push --force origin feat/P01.01-x", "git push -f", "git push origin :claim/P01.01",
                     "git commit --no-verify -m x", "gh auth switch --user Demidoga",
                     'git config user.email "x@y.z"', "gh pr create --base main",
                     "python harness/verification/scd.py gh -- api -X DELETE repos/o/r/branches/main/protection",
                     "python harness/verification/scd.py gh -- pr merge 3 --admin",
                     "SCD_HARNESS_MAINTENANCE=1 claude"]:
            with self.subTest(line=line):
                self.assertEqual(self.decide("Bash", command=line), "deny")

    def test_ordinary_commands_allowed(self):
        self.branch("feat/P01.01-x")
        for line in ["git push -u origin feat/P01.01-x", "git push origin docs/P00.03-dev-notes",
                     "git config user.email", "python harness/verification/scd.py gh -- pr create --base dev",
                     "git commit -m 'docs: x'", "gh auth status"]:
            with self.subTest(line=line):
                self.assertEqual(self.decide("Bash", command=line), "allow")

    def test_approval_asks_but_merge_does_not(self):
        self.assertEqual(self.decide("Bash", command=GH + "pr review 2 --approve"), "ask")
        self.assertEqual(self.decide("Bash", command=GH + "pr merge 2 --merge"), "allow")

    def test_secret_in_staged_changes(self):
        self.branch("feat/P01.01-x")
        (self.repo / "notes.txt").write_text(FAKE_TOKEN)
        sh(self.repo, "git", "add", "notes.txt")
        self.assertEqual(self.decide("Bash", command="git commit -m x"), "deny")
        with self.assertRaises(scd.Failure):
            scd.check_secret_scan(self.repo)


class Edits(Fixture):
    def edit(self, rel, content="text"):
        return self.decide("Write", file_path=str(self.repo / rel), content=content)

    def test_edit_on_main_denied(self):
        self.assertEqual(self.edit("docs/x.md"), "deny")

    def test_protected_and_secret_and_phase0(self):
        self.done("P00.01")
        self.branch("docs/P00.03-x")
        self.assertEqual(self.edit("docs/source/Semester_Project_Guide.pdf"), "deny")
        self.assertEqual(self.edit("harness/verification/scd.py"), "deny")
        self.assertEqual(self.edit(".claude/settings.json"), "deny")
        self.assertEqual(self.edit("docs/a.md", FAKE_TOKEN), "deny")
        self.assertEqual(self.edit("services/verdict/engine.py"), "deny")
        self.assertEqual(self.edit("docs/a.md"), "allow")

    def test_blocked_task_and_scope(self):
        self.done("P00")
        self.branch("feat/P01.04-deploy")  # needs P01.01-03
        self.assertEqual(self.edit("k8s/a.yaml"), "deny")
        self.done("P01.01", "P01.02", "P01.03")
        self.assertEqual(self.edit("k8s/a.yaml"), "allow")
        self.assertEqual(self.edit("services/verdict/a.py"), "deny")  # outside P01.04 scope

    def test_hook_output_is_a_denial(self):
        event = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push origin main"}})
        out = subprocess.run([sys.executable, str(ROOT / "harness/verification/scd.py"), "hook", "pre-tool"],
                             input=event, capture_output=True, text=True,
                             env={**os.environ, "CLAUDE_PROJECT_DIR": str(self.repo)})
        self.assertEqual(json.loads(out.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")


class PullRequests(Fixture):
    def problems(self, head, author, changed):
        return scd.pr_task_problems(self.repo, self.policy, head, "dev", author, changed)

    def test_wrong_targets(self):
        for base, head, same in [("main", "feat/P01.01-x", True), ("main", "dev", False),
                                 ("release", "dev", True), ("dev", "random-branch", True)]:
            self.assertTrue(scd.branch_problems(self.policy, base, head, same), (base, head))
        self.assertEqual(scd.branch_problems(self.policy, "main", "dev", True), [])
        self.assertEqual(scd.branch_problems(self.policy, "dev", "feat/P01.01-x", True), [])

    def test_blocked_owner_scope_handoff(self):
        found = " | ".join(self.problems("feat/P01.01-x", "intruder", ["services/verdict/a.py"]))
        for expected in ["dependency P00", "belongs to", "outside P01.01 scope", "handoff not updated",
                         "AI-usage log"]:
            self.assertIn(expected, found)

    def test_clean_task_pr(self):
        self.done("P00")
        self.publish_dev()
        changed = ["k8s/a.yaml", "docs/handoff/Demidoga.md", "docs/submission/AIUsageLog.md"]
        self.assertEqual(self.problems("feat/P01.01-x", "Demidoga", changed), [])
        self.done("P01.02")  # claiming another task's completion
        changed.append(f"{scd.STATUS_DIR}/P01.02.json")
        self.assertIn("another task", self.problems("feat/P01.01-x", "Demidoga", changed)[0])

    def test_protected_change_needs_label_and_base_policy_wins(self):
        self.branch("fix/P00.04-x")
        loosened = dict(self.policy, protected_paths=[])
        self.write(scd.POLICY_PATH, loosened)
        sh(self.repo, "git", "commit", "-qam", "loosen")
        old = os.environ.copy()
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(old)))
        os.environ.update(PR_BASE="dev", PR_LABELS="")
        with self.assertRaisesRegex(scd.Failure, "label from a human"):
            scd.check_protected_files(self.repo)
        os.environ["PR_LABELS"] = self.policy["protected_label"]
        scd.check_protected_files(self.repo)

    def test_requirement_rewording_detected(self):
        self.branch("docs/P00.01-x")
        data = self.read(scd.REQS_PATH)
        data["requirements"][0]["statement"] = "weakened"
        self.write(scd.REQS_PATH, data)
        self.assertIn("reworded", scd.requirement_text_changes(self.repo, "dev")[0])

    def test_modified_source_document(self):
        pdf = self.repo / "docs/source/a.pdf"
        pdf.write_bytes(b"original")
        (self.repo / self.policy["source_checksums"]).write_text(
            hashlib.sha256(b"original").hexdigest() + "  a.pdf\n")
        pdf.write_bytes(b"tampered")
        with self.assertRaisesRegex(scd.Failure, "modified"):
            scd.check_protected_files(self.repo)

    def test_failing_or_skipped_checks_block(self):
        names = self.policy["required_checks"]
        good = {n: "success" for n in names}
        self.assertEqual(scd.gate_problems(good, names), [])
        for bad in ("failure", "skipped", "cancelled"):
            self.assertTrue(scd.gate_problems({**good, "lint": bad}, names))
        self.assertTrue(scd.gate_problems({}, names))


class TasksAndClaims(Fixture):
    def test_phase0_blocks_application_code(self):
        (self.repo / "services/verdict").mkdir(parents=True)
        (self.repo / "services/verdict/engine.py").write_text("x = 1\n")
        with self.assertRaisesRegex(scd.Failure, "not allowed in Phase 0"):
            scd.check_task_policy(self.repo)

    def test_premature_completion(self):
        self.done("P01")
        self.assertIn("dependency", scd.status_problems(self.repo)[0])
        self.write(f"{scd.STATUS_DIR}/P00.01.json", {"status": "done", "pr": "x", "evidence": []})
        self.assertTrue(any("evidence" in p for p in scd.status_problems(self.repo)))
        data = self.read(scd.REQS_PATH)
        data["requirements"][0]["status"] = "verified"
        self.write(scd.REQS_PATH, data)
        with self.assertRaisesRegex(scd.Failure, "without evidence"):
            scd.check_requirements_registry(self.repo)

    def test_missing_acceptance_and_cycle(self):
        data = self.read(scd.TASKS_PATH)
        tasks = {t["id"]: t for t in data["tasks"]}
        tasks["P01.01"]["acceptance"] = ""
        tasks["P00.01"]["depends_on"] = ["P00"]
        self.write(scd.TASKS_PATH, data)
        found = " ".join(scd.task_graph_problems(self.repo))
        self.assertIn("missing acceptance", found)
        self.assertIn("cycle", found)

    def test_gated_check_cannot_pass_empty(self):
        self.assertIn("NOT APPLICABLE", scd.check_gated(self.repo, "verdict-unit-tests"))
        self.done("P03")
        with self.assertRaisesRegex(scd.Failure, "gate P03 is passed"):
            scd.check_gated(self.repo, "verdict-unit-tests")

    def test_code_without_tests_fails(self):
        (self.repo / "services/verdict").mkdir(parents=True)
        (self.repo / "services/verdict/engine.py").write_text("x = 1\n")
        with self.assertRaisesRegex(scd.Failure, "command failed"):
            scd.check_gated(self.repo, "verdict-unit-tests")

    def test_blocked_wrong_owner_and_duplicate_claim(self):
        with self.assertRaisesRegex(scd.Failure, "blocked by P00"):
            scd.claim(self.repo, "P01.01")
        with self.assertRaisesRegex(scd.Failure, "assigned to the primary"):
            scd.claim(self.repo, "P01.02")
        self.done("P00")
        self.publish_dev()
        self.assertIn("claimed P01.01", scd.claim(self.repo, "P01.01"))
        other = self.tmp / "second" / "SCD_Proj"
        sh(self.tmp, "git", "clone", "-q", "-b", "dev", self.remote.as_posix(), str(other))
        self.configure(other)
        with self.assertRaisesRegex(scd.Failure, "already claimed"):
            scd.claim(other, "P01.01")

    def test_gate_closes_a_phase_in_one_pull_request(self):
        tasks = scd.tasks_by_id(self.repo)
        members = [f"P00.0{n}" for n in range(1, 7)]
        self.done(*members, status="in_review")
        self.publish_dev("all in review")
        self.done(*members, "P00")
        owner = self.policy["identities"][tasks["P00"]["owner"]]
        changed = [f"{scd.STATUS_DIR}/{t}.json" for t in [*members, "P00"]]
        changed += ["docs/planning/ImplementationPlan.md", owner["handoff"], self.policy["ai_usage_log"]]
        self.assertEqual(scd.pr_task_problems(self.repo, self.policy, "docs/P00-gate", "dev", owner["login"],
                                              changed), [])
        (self.repo / f"{scd.STATUS_DIR}/P00.06.json").unlink()  # a missing member still blocks the gate
        found = scd.pr_task_problems(self.repo, self.policy, "docs/P00-gate", "dev", owner["login"], changed)
        self.assertIn("dependency P00.06", found[0])

    def test_phase_can_be_closed_task_by_task(self):
        """Recording each task done regenerates the plan; every such pull request, and the gate, must pass."""
        tasks = scd.tasks_by_id(self.repo)
        members = [f"P00.0{n}" for n in range(1, 7)]
        self.done(*members, status="in_review")
        scd.render(self.repo)
        self.publish_dev("all in review")
        for tid in [*members, "P00"]:
            with self.subTest(task=tid):
                owner = self.policy["identities"][tasks[tid]["owner"]]
                self.done(tid)
                stale = scd.render(self.repo, write=False)
                scd.render(self.repo)
                self.assertIn("docs/planning/ImplementationPlan.md", stale)
                changed = [f"{scd.STATUS_DIR}/{tid}.json", *stale, owner["handoff"], self.policy["ai_usage_log"]]
                # the fixture lacks the other generated documents; only the plan depends on task status
                changed = [f for f in changed if f == "docs/planning/ImplementationPlan.md" or f not in stale]
                self.assertEqual(scd.pr_task_problems(self.repo, self.policy, f"docs/{tid}-record", "dev",
                                                      owner["login"], changed), [])
                self.publish_dev(f"{tid} done")
        self.assertEqual(scd.status_problems(self.repo), [])
        self.assertIn("P00", scd.done_tasks(self.repo))

    def test_invalid_contract(self):
        try:
            import jsonschema  # noqa: F401
            import openapi_spec_validator  # noqa: F401
        except ImportError:
            self.skipTest("contract libraries not installed")
        scd.check_contract_tests(self.repo)
        bad = self.repo / "contracts/schemas/examples/verdict.valid.json"
        data = json.loads(bad.read_text())
        data["verdict"] = "MAYBE"
        bad.write_text(json.dumps(data))
        with self.assertRaisesRegex(scd.Failure, "MAYBE"):
            scd.check_contract_tests(self.repo)


class ReviewFindings(Fixture):
    """One test per bypass the independent review of pull request 8 demonstrated."""

    def with_env(self, **values):
        old = os.environ.copy()
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(old)))
        os.environ.update(values)

    def test_h1_branch_cannot_rewrite_the_rules_judging_it(self):
        self.done("P00")
        self.publish_dev()
        self.branch("feat/P01.02-x")
        data = self.read(scd.TASKS_PATH)
        for task in data["tasks"]:
            if task["id"] == "P01.02":
                task.update(allowed_paths=["**"], depends_on=[], owner="secondary")
        self.write(scd.TASKS_PATH, data)
        found = " | ".join(scd.pr_task_problems(self.repo, self.policy, "feat/P01.02-x", "dev", "Demidoga",
                                                 ["contracts/openapi/critic.json"]))
        self.assertIn("belongs to Abdullah-SE-bit", found)
        self.assertIn("outside P01.02 scope", found)
        self.assertIn(scd.TASKS_PATH.split("/")[-1], str(self.policy["protected_paths"]))

    def test_h2_bootstrap_name_gives_no_exemption(self):
        name = self.policy["branches"]["bootstrap"]
        self.assertTrue(scd.branch_problems(self.policy, "dev", name, True))
        self.branch(name)
        self.with_env(PR_BASE="dev", PR_HEAD=name, PR_AUTHOR="intruder")
        with self.assertRaisesRegex(scd.Failure, "must look like"):
            scd.check_task_policy(self.repo)

    def test_h2_self_certification_is_rejected(self):
        self.write(f"{scd.STATUS_DIR}/P00.01.json",
                   {"status": "done", "pr": "https://example.invalid", "evidence": ["https://example.invalid"]})
        found = " | ".join(scd.status_problems(self.repo))
        for expected in ["pr must link", "not in this repository"]:
            self.assertIn(expected, found)

    def test_done_needs_the_human_label(self):
        self.branch("docs/P00-gate")
        self.done("P00.01")
        sh(self.repo, "git", "add", "-A")
        sh(self.repo, "git", "commit", "-qm", "complete")
        self.with_env(PR_BASE="dev", PR_LABELS="")
        with self.assertRaisesRegex(scd.Failure, "label from a human"):
            scd.check_protected_files(self.repo)
        os.environ["PR_LABELS"] = self.policy["protected_label"]
        scd.check_protected_files(self.repo)

    def test_h3_bypasses_are_denied_or_asked(self):
        self.branch("feat/P01.01-x")
        for line in [GH + "api repos/O/R/pulls/8/reviews -f event=APPROVE",
                     GH + "api -X PUT repos/O/R/pulls/8/merge",
                     GH + "api graphql -f query='mutation { deleteBranchProtectionRule }'",
                     GH + "pr edit 8 --add-label authorized-protected-change",
                     GH + 'pr create --label "authorized-protected-change"']:
            with self.subTest(line=line):
                self.assertEqual(self.decide("Bash", command=line), "deny")
        for line in [GH + 'pr review 8 --body "ok; done" --approve', GH + "pr review 8 -a",
                     GH + "pr edit 8 --add-label task"]:
            with self.subTest(line=line):
                self.assertEqual(self.decide("PowerShell", command=line), "ask")
        self.assertEqual(self.decide("Bash", command=GH + "api repos/O/R/branches/main/protection"), "allow")

    def test_h3_wrapper_refuses_without_the_hook(self):
        with self.assertRaisesRegex(scd.Failure, "API writes"):
            scd.gh(self.repo, ["api", "-X", "PUT", "repos/O/R/pulls/8/merge"])

    def test_h4_local_settings_and_shell_writes(self):
        local = str(self.repo / ".claude/settings.local.json")
        self.assertEqual(self.decide("Write", file_path=local, content="{}"), "deny")
        for line in ["echo x > .claude/settings.local.json", "sed -i s/a/b/ harness/verification/scd.py",
                     "echo x > .github/workflows/pr-checks.yml",
                     "Set-Content harness\\policies\\project.json x", "rm -rf .claude/hooks"]:
            with self.subTest(line=line):
                self.assertEqual(self.decide("Bash", command=line), "deny")
        self.assertEqual(self.decide("Bash", command="python harness/verification/scd.py check lint > out.txt"),
                         "allow")
        self.assertEqual(self.decide("mcp__serena__serena_repl", code="x"), "ask")

    def test_m8_guard_gaps(self):
        self.branch("feat/P01.01-x")
        for line in ["git -c user.email=a@b.c commit -m x", "GIT_AUTHOR_EMAIL=a@b.c git commit -m x",
                     "git switch dev && git commit -m x", "git push origin +feat/P01.01-x",
                     "git push -uf origin feat/P01.01-x", 'git push origin "main"', "gh.exe pr list",
                     "gh pr create # scd.py"]:
            with self.subTest(line=line):
                self.assertEqual(self.decide("Bash", command=line), "deny")
        (self.repo / "config/README.md").parent.mkdir(exist_ok=True)
        tracked = self.repo / "harness/coordination/message.schema.json"
        tracked.write_text(FAKE_TOKEN)
        self.assertEqual(self.decide("Bash", command="git commit -am x"), "deny")

    def test_h6_review_states(self):
        tasks = scd.tasks_by_id(self.repo)
        self.assertEqual(scd.unmet_dependencies(tasks, "P00.04", {"P00.01": "in_review"}), [])
        gate = scd.unmet_dependencies(tasks, "P00", {t: "in_review" for t in tasks})
        self.assertIn("P00.01", gate)
        self.assertTrue(scd.unmet_dependencies(tasks, "P01.01", {"P00": "in_review"}))
        self.done("P00.02", status="in_review")
        self.assertEqual(scd.done_tasks(self.repo), set())

    def test_status_files_of_others(self):
        tasks = scd.tasks_by_id(self.repo)
        path = f"{scd.STATUS_DIR}/P00.02.json"

        def allowed(branch_task, before):
            return scd.status_change_allowed(self.repo, tasks, branch_task, path, before)

        self.done("P00.02", status="in_review")
        self.assertFalse(allowed("P00.01", {}))  # creating another task's record unblocks dependants
        self.assertTrue(allowed("P00.01", {"P00.02": "done"}))  # downgrade
        self.assertTrue(allowed("P00.02", {}))  # own
        self.assertTrue(allowed("P00", {}))  # phase gate
        self.done("P00.02")
        self.assertFalse(allowed("P00.01", {"P00.02": "in_review"}))  # raising
        (self.repo / path).unlink()
        self.assertFalse(allowed("P00.01", {"P00.02": "done"}))  # deleting

    def test_gh_flag_shapes_from_second_review(self):
        self.branch("feat/P01.01-x")
        deny = ["api repos/O/R/pulls/8/reviews -fevent=APPROVE", "api repos/O/R/pulls/8/merge -X=PUT",
                "api repos/O/R/pulls/8/merge -iXPUT", "api graphql -Fquery=@m.graphql",
                "api -H X:y repos/O/R", "pr create -lauthorized-protected-change",
                "pr create -l=authorized-protected-change", "pr create -dlAUTHORIZED-PROTECTED-CHANGE",
                "pr edit 8 --add-label task,authorized-protected-change", "pr merge 8 --admin",
                "pr close 8 --delete-branch", "pr close 8 -d", "secret set X", "extension install a/b",
                "pr --web review 8"]
        ask = ["pr review 8 -ab ok", "pr --repo O/R review 8 --approve",
               "pr review 8 --comment -a", "pr review 8 -r -b no", "pr create -l task"]
        allow = ["api repos/O/R/pulls/8 -q .state", "api --paginate repos/O/R/pulls",
                 "pr review 8 --comment --body-file notes.md", 'pr create --body "about authorized-protected-change"',
                 "pr view 8 --json labels", "pr checks 8 --watch 2>&1"]
        for expected, lines in (("deny", deny), ("ask", ask), ("allow", allow)):
            for line in lines:
                with self.subTest(line=line):
                    self.assertEqual(self.decide("Bash", command=GH + line), expected)
        self.assertEqual(self.decide("Bash", command='G="' + GH.strip() + '"; $G pr -R O/R review 8 -a'), "ask")
        two_lines = GH + "api repos/O/R/pulls/8\ngit status"
        self.assertEqual(self.decide("Bash", command=two_lines), "allow")
        self.assertEqual(self.decide("Bash", command=GH + "pr view 8\n" + GH + "pr review 8 -a"), "ask")
        with self.assertRaisesRegex(scd.Failure, "API writes"):
            scd.gh(self.repo, ["api", "repos/O/R/pulls/8/merge", "-iXPUT"])

    def test_wrapped_and_quoted_decisions_still_ask(self):
        script = "python harness/verification/scd.py "
        for line in [script + '"gh" -- pr review 8 --approve', script + "'gh' -- pr review 8 --approve",
                     script + "g\\h -- pr review 8 --approve", f'bash -c "{GH}pr review 8 --approve"',
                     f'eval "{GH}pr review 8 -a"',
                     f'bash -c "{GH}pr review 8 -ab ok"', f"pwsh -Command '{GH}pr -R O/R review 8 -a'",
                     f'bash -c "{GH}pr review 8 --request-changes"']:
            with self.subTest(line=line):
                self.assertEqual(self.decide("Bash", command=line), "ask")
        self.assertEqual(self.decide("Bash", command="git log --author=Asad --oneline"), "allow")
        self.assertEqual(self.decide("PowerShell", command="Rename-Item .claude/hooks/guard.py x.py"), "deny")

    def test_other_tools_are_checked(self):
        self.branch("feat/P01.01-x")
        line = GH + "pr review 8 --approve; git push origin main"
        for tool in ("Monitor", "mcp__terminal__run_in_terminal"):
            self.assertEqual(self.decide(tool, command=line), "deny")
        for tool in ("mcp__serena__create_text_file", "mcp__filesystem__write_file"):
            self.assertEqual(self.decide(tool, relative_path="harness/verification/scd.py", content="x"), "deny")
        self.assertEqual(self.decide("mcp__serena__find_symbol", relative_path="harness/verification/scd.py"), "allow")
        self.assertIn("Monitor", (ROOT / ".claude/settings.json").read_text(encoding="utf-8"))

    def test_one_line_shell_writes_and_identity(self):
        self.branch("feat/P01.01-x")
        for line in ["sed --in-place s/a/b/ harness/verification/scd.py",
                     "cd harness/verification && sed -i s/a/b/ scd.py",
                     "git restore --source=HEAD~1 -- .github/workflows/pr-checks.yml",
                     "git checkout main -- .github/workflows/pr-checks.yml",
                     "New-Item -Force .claude/hooks/guard.py", "[IO.File]::WriteAllText('pyproject.toml','')",
                     "curl -o requirements-dev.txt https://example.com", "git commit --author='A <a@b.c>' -m x",
                     "git --config-env=user.email=X commit -m x"]:
            with self.subTest(line=line):
                self.assertEqual(self.decide("Bash", command=line), "deny")
        for line in ["git log 2>/dev/null -- .github/workflows", "git checkout feat/P01.01-x"]:
            with self.subTest(line=line):
                self.assertEqual(self.decide("Bash", command=line), "allow")
        (self.repo / "new.txt").write_text(FAKE_TOKEN)
        self.assertEqual(self.decide("Bash", command="git add new.txt && git commit -m x"), "deny")


if __name__ == "__main__":
    unittest.main()
