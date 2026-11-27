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

    def done(self, *ids):
        for tid in ids:
            self.write(f"{scd.STATUS_DIR}/{tid}.json",
                       {"status": "done", "pr": "https://example.com/1", "evidence": ["https://example.com/e"]})

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

    def test_approval_and_merge_ask_a_human(self):
        for line in ["python harness/verification/scd.py gh -- pr review 2 --approve",
                     "python harness/verification/scd.py gh -- pr merge 2 --merge"]:
            self.assertEqual(self.decide("Bash", command=line), "ask")

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


if __name__ == "__main__":
    unittest.main()
