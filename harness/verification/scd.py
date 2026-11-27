#!/usr/bin/env python3
"""SCD harness: CI checks, Claude hooks, task claims, identity and document rendering.

Standard library only, except the contract check (jsonschema, openapi-spec-validator).
Run from inside the repository: python harness/verification/scd.py <command>
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess  # nosec B404
import sys
from pathlib import Path
from typing import Any

POLICY_PATH = "harness/policies/project.json"
REQS_PATH = "docs/requirements/requirements.json"
TASKS_PATH = "harness/task-registry/tasks.json"
STATUS_DIR = "harness/task-registry/status"
MODULES = {f"M{n}" for n in range(1, 15)} | {"M6i", "M10t"}
SECRET_PATTERNS = [
    r"gh[pousr]_[A-Za-z0-9]{30,}", r"github_pat_[A-Za-z0-9_]{40,}", r"sk-ant-[A-Za-z0-9_-]{20,}",
    r"\bsk-[A-Za-z0-9]{32,}", r"AKIA[0-9A-Z]{16}", r"AIza[0-9A-Za-z_-]{35}", r"\bhf_[A-Za-z0-9]{30,}",
    r"\bgsk_[A-Za-z0-9]{40,}", r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
]


class Failure(Exception):
    """A check failed; the message lists why."""


# ---------------------------------------------------------------- basics

def run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")  # nosec B603


def git(root: Path, *args: str) -> str:
    return run(["git", *args], root).stdout.strip()


def find_root(start: str | None = None) -> Path:
    top = run(["git", "rev-parse", "--show-toplevel"], Path(start or os.getcwd())).stdout.strip()
    if not top:
        raise Failure("not inside a git repository")
    return Path(top)


def load(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def matches(path: str, pattern: str) -> bool:
    """Glob where ** crosses directories and * does not."""
    regex = re.escape(pattern).replace(r"\*\*/", "(?:.*/)?").replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.fullmatch(regex, path) is not None


def match_any(path: str, patterns: list[str]) -> bool:
    return any(matches(path, p) for p in patterns)


def repo_files(root: Path) -> list[str]:
    """Tracked plus untracked-but-not-ignored files."""
    out = git(root, "ls-files", "--cached", "--others", "--exclude-standard")
    return sorted(f for f in out.splitlines() if (root / f).is_file())


def require(problems: list[str]) -> None:
    if problems:
        raise Failure("\n".join(f"  - {p}" for p in problems))


def policy_for(root: Path, base: str | None = None) -> dict[str, Any]:
    """Policy from the base branch when it has one, so a PR cannot loosen the rules it is judged by."""
    if base:
        shown = run(["git", "show", f"origin/{base}:{POLICY_PATH}"], root)
        if shown.returncode == 0:
            return json.loads(shown.stdout)
    return load(root, POLICY_PATH)


# ---------------------------------------------------------------- tasks and phases

def tasks_by_id(root: Path, ref: str | None = None) -> dict[str, dict[str, Any]]:
    """Tasks as the given ref defines them, so a branch cannot rewrite the rules it is judged by."""
    if ref:
        shown = run(["git", "show", f"{ref}:{TASKS_PATH}"], root)
        if shown.returncode == 0:
            return {t["id"]: t for t in json.loads(shown.stdout)["tasks"]}
    return {t["id"]: t for t in load(root, TASKS_PATH)["tasks"]}


def task_states(root: Path, ref: str | None = None) -> dict[str, str]:
    """task id -> status: 'in_review' (merged, awaiting the other contributor) or 'done' (reviewed)."""
    if ref:
        listing = git(root, "ls-tree", "--name-only", ref, f"{STATUS_DIR}/").splitlines()
        texts = {Path(p).stem: git(root, "show", f"{ref}:{p}") for p in listing if p.endswith(".json")}
    else:
        texts = {p.stem: p.read_text(encoding="utf-8") for p in (root / STATUS_DIR).glob("*.json")}
    return {tid: json.loads(text).get("status", "") for tid, text in texts.items()}


def done_tasks(root: Path, ref: str | None = None) -> set[str]:
    return {tid for tid, state in task_states(root, ref).items() if state == "done"}


def unmet_dependencies(tasks: dict[str, dict[str, Any]], task_id: str, states: dict[str, str]) -> list[str]:
    """A dependency must be reviewed; within one phase, merged work awaiting review also unblocks (never a gate)."""
    def met(dep: str) -> bool:
        if states.get(dep) == "done":
            return True
        return ("." in task_id and states.get(dep) == "in_review"
                and tasks[dep]["phase"] == tasks[task_id]["phase"])

    return [d for d in tasks[task_id]["depends_on"] if not met(d)]


def application_files(policy: dict[str, Any], files: list[str]) -> list[str]:
    roots = [r + "/**" for r in policy["application_roots"]]
    code = (".py", ".ts", ".tsx", ".js", ".jsx", ".sql", ".go", ".rs", ".java")
    found = []
    for f in files:
        name = f.rsplit("/", 1)[-1]
        if match_any(f, roots) and name not in policy["non_application_files"]:
            found.append(f)
        elif f.endswith(code) and not match_any(f, ["harness/**", ".claude/**", "scripts/**"]):
            found.append(f)
    return found


# ---------------------------------------------------------------- checks

def check_repo_structure(root: Path) -> str:
    policy = load(root, POLICY_PATH)
    required = load(root, "harness/policies/required-files.json")["files"]
    problems = [f"missing or empty: {f}" for f in required
                if not (root / f).is_file() or (root / f).stat().st_size == 0]
    for f in repo_files(root):
        if f.endswith(".json"):
            try:
                load(root, f)
            except ValueError as exc:
                problems.append(f"invalid JSON {f}: {exc}")
    workflow = (root / ".github/workflows/pr-checks.yml").read_text(encoding="utf-8")
    matrix = re.search(r"check: \[([^\]]+)\]", workflow)
    jobs = {c.strip() for c in matrix.group(1).split(",")} if matrix else set()
    jobs |= set(re.findall(r"^  (ci-gate):\s*$", workflow, re.M))
    for name in policy["required_checks"]:
        if name not in jobs:
            problems.append(f"required check '{name}' has no job in pr-checks.yml")
    problems += [f"pr-checks.yml runs unknown check '{j}'" for j in sorted(jobs - set(policy["required_checks"]))]
    if "continue-on-error" in workflow:
        problems.append("pr-checks.yml must not use continue-on-error")
    for wf in (root / ".github/workflows").glob("*.yml"):
        for action in re.findall(r"uses:\s*(\S+)", wf.read_text(encoding="utf-8")):
            if not re.search(r"@[0-9a-f]{40}$", action):
                problems.append(f"{wf.name}: action not pinned to a commit SHA: {action}")
    problems += [f"stale generated document (run 'scd.py render'): {p}" for p in render(root, write=False)]
    require(problems)
    return f"{len(required)} required files, {len(jobs)} CI jobs"


def check_requirements_registry(root: Path) -> str:
    reqs = load(root, REQS_PATH)["requirements"]
    pages = {"Semester_Project_Description.pdf": 6, "Semester_Project_Guide.pdf": 8}
    fields = ["id", "document", "page", "section", "module", "category", "level", "statement",
              "acceptance", "verification", "depends_on", "status", "evidence"]
    ids = [r.get("id") for r in reqs]
    problems = [f"duplicate id {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for r in reqs:
        rid = r.get("id", "?")
        problems += [f"{rid}: missing field {f}" for f in fields if f not in r or r[f] in ("", None)]
        if r.get("document") not in pages or not 1 <= r.get("page", 0) <= pages.get(r.get("document"), 0):
            problems.append(f"{rid}: bad source document or page")
        if r.get("module") not in MODULES:
            problems.append(f"{rid}: unknown module {r.get('module')}")
        if r.get("level") not in ("mandatory", "recommended", "optional"):
            problems.append(f"{rid}: bad level")
        if r.get("status") not in ("unimplemented", "in_progress", "implemented", "verified"):
            problems.append(f"{rid}: bad status")
        if r.get("status") in ("implemented", "verified"):
            if not r.get("evidence"):
                problems.append(f"{rid}: claims {r['status']} without evidence")
            problems += [f"{rid}: evidence file missing: {e}" for e in r.get("evidence", [])
                         if not e.startswith("https://") and not (root / e).exists()]
        problems += [f"{rid}: unknown dependency {d}" for d in r.get("depends_on", []) if d not in ids]
    problems += [f"module {m} has no requirement" for m in sorted(MODULES - {r.get("module") for r in reqs})]
    problems += [f"user requirement U{n} missing" for n in range(1, 11) if f"USR-{n:03d}" not in ids]
    require(problems)
    return f"{len(reqs)} requirements, all 16 modules, U1-U10"


def check_traceability(root: Path) -> str:
    reqs = {r["id"]: r for r in load(root, REQS_PATH)["requirements"]}
    tasks = tasks_by_id(root)
    covered: dict[str, list[str]] = {}
    problems = []
    for tid, t in tasks.items():
        for rid in t["requirements"]:
            if rid not in reqs:
                problems.append(f"{tid}: unknown requirement {rid}")
            covered.setdefault(rid, []).append(tid)
    problems += [f"mandatory requirement {r} has no task" for r, v in reqs.items()
                 if v["level"] == "mandatory" and r not in covered]
    done = done_tasks(root)
    problems += [f"{r}: marked verified but no covering task is done" for r, v in reqs.items()
                 if v["status"] == "verified" and not done.intersection(covered.get(r, []))]
    require(problems)
    return f"{len(covered)} requirements mapped to {len(tasks)} tasks"


def task_graph_problems(root: Path) -> list[str]:
    raw = load(root, TASKS_PATH)["tasks"]
    tasks = {t["id"]: t for t in raw}
    problems = [f"duplicate task id {t}" for t in tasks if sum(x["id"] == t for x in raw) > 1]
    fields = ["title", "description", "requirements", "module", "owner", "reviewer", "complexity",
              "allowed_paths", "deliverables", "acceptance", "tests", "verification_commands",
              "evidence", "definition_of_done"]
    for tid, t in tasks.items():
        problems += [f"{tid}: missing {f}" for f in fields if not t.get(f)]
        problems += [f"{tid}: unknown dependency {d}" for d in t.get("depends_on", []) if d not in tasks]
        if t.get("owner") == t.get("reviewer"):
            problems.append(f"{tid}: owner cannot review own work")
        if "." not in tid:
            members = [m for m in tasks if m.startswith(tid + ".")]
            problems += [f"{tid}: gate does not depend on {m}" for m in members if m not in t["depends_on"]]
    seen: dict[str, int] = {}

    def visit(node: str) -> None:
        if seen.get(node) == 2 or node not in tasks:
            return
        if seen.get(node) == 1:
            problems.append(f"dependency cycle through {node}")
            return
        seen[node] = 1
        for d in tasks[node].get("depends_on", []):
            visit(d)
        seen[node] = 2

    for tid in tasks:
        visit(tid)
    return problems


def status_problems(root: Path) -> list[str]:
    tasks, states = tasks_by_id(root), task_states(root)
    policy = load(root, POLICY_PATH)
    ours = f"https://github.com/{policy['repository']}/"
    problems = []
    for tid in sorted(states):
        if tid not in tasks:
            problems.append(f"status file for unknown task {tid}")
            continue
        record = load(root, f"{STATUS_DIR}/{tid}.json")
        problems += [f"{tid} marked {states[tid]} but dependency {d} is not met"
                     for d in unmet_dependencies(tasks, tid, states)]
        if states[tid] not in ("in_review", "done") or not record.get("evidence"):
            problems.append(f"{tid}: status must be in_review or done, with evidence")
        if not str(record.get("pr", "")).startswith(ours):
            problems.append(f"{tid}: pr must link a pull request of this repository")
        for item in record.get("evidence", []):
            if item.startswith("https://"):
                if not item.startswith(ours):
                    problems.append(f"{tid}: evidence link is not in this repository: {item}")
            elif not (root / item).exists():
                problems.append(f"{tid}: evidence missing: {item}")
        if states[tid] == "done":
            owner = policy["identities"][tasks[tid]["owner"]]["login"]
            logins = {i["login"] for i in policy["identities"].values()}
            if record.get("reviewed_by") not in logins - {owner}:
                problems.append(f"{tid}: done needs reviewed_by, the contributor who is not {owner}")
            if not str(record.get("review", "")).startswith(ours):
                problems.append(f"{tid}: done needs a review link")
    return problems


def status_change_allowed(root: Path, tasks: dict[str, dict[str, Any]], tid: str, path: str) -> bool:
    """Own status; withdrawing a claim of completion; or a phase gate recording its own phase."""
    other = Path(path).stem
    if other == tid or not (root / path).exists():
        return True
    if load(root, path).get("status") == "in_review":
        return True
    return "." not in tid and other in tasks and tasks[other]["phase"] == tasks[tid]["phase"]


def pr_task_problems(root: Path, policy: dict[str, Any], head: str, base: str, author: str,
                     changed: list[str]) -> list[str]:
    """Rules for one pull request into dev, judged against the task registry of the base branch."""
    found = re.match(policy["branches"]["task_pattern"], head)
    if not found:
        return [f"branch '{head}' must look like feat/P01.01-short-name"]
    tid = found.group(2)
    tasks = tasks_by_id(root, f"origin/{base}")
    if tid not in tasks:
        return [f"unknown task {tid}"]
    task, identity = tasks[tid], policy["identities"][tasks[tid]["owner"]]
    problems = [f"{tid} blocked: dependency {d} is not met on {base}"
                for d in unmet_dependencies(tasks, tid, task_states(root, f"origin/{base}"))]
    if author and author != identity["login"]:
        problems.append(f"{tid} belongs to {identity['login']}, PR author is {author}")
    allowed = task["allowed_paths"] + policy["always_allowed_paths"]
    problems += [f"outside {tid} scope: {f}" for f in changed if not match_any(f, allowed)]
    if identity["handoff"] not in changed:
        problems.append(f"handoff not updated: {identity['handoff']}")
    if policy["ai_usage_log"] not in changed:
        problems.append(f"AI-usage log not updated: {policy['ai_usage_log']}")
    problems += [f"cannot mark another task done: {f}" for f in changed
                 if f.startswith(STATUS_DIR + "/") and not status_change_allowed(root, tasks, tid, f)]
    return problems


def changed_files(root: Path, base: str) -> list[str]:
    ref = f"origin/{base}"
    if run(["git", "rev-parse", "--verify", ref], root).returncode:
        raise Failure(f"cannot resolve {ref}; fetch it first")
    return git(root, "diff", "--name-only", "--no-renames", f"{ref}...HEAD").splitlines()


def check_task_policy(root: Path) -> str:
    base, head = os.environ.get("PR_BASE"), os.environ.get("PR_HEAD", "")
    policy = policy_for(root, base)
    problems = task_graph_problems(root) + status_problems(root)
    if "P00" not in done_tasks(root, f"origin/{base}" if base else None):
        problems += [f"application implementation is not allowed in Phase 0: {f}"
                     for f in application_files(policy, repo_files(root))]
    bootstrapping = (head == policy["branches"]["bootstrap"]
                     and run(["git", "cat-file", "-e", f"origin/{base}:{POLICY_PATH}"], root).returncode != 0)
    syncing = head == "main" and os.environ.get("PR_SAME_REPO", "true") == "true"
    if base == "dev" and not bootstrapping and not syncing:
        problems += pr_task_problems(root, policy, head, base, os.environ.get("PR_AUTHOR", ""),
                                     changed_files(root, base))
    require(problems)
    return "task graph, statuses and phase rules hold"


def branch_problems(policy: dict[str, Any], base: str, head: str, same_repo: bool) -> list[str]:
    if base == "main":
        return [] if head == "dev" and same_repo else ["pull requests into main must come from this repository's dev"]
    if base == "dev":
        if head == "main" and same_repo:
            return []  # syncing main back into dev
        if re.match(policy["branches"]["task_pattern"], head):
            return []
        return [f"branch '{head}' must look like feat/P01.01-short-name"]
    return [f"pull requests must target dev (or main from dev), not '{base}'"]


def check_branch_policy(root: Path) -> str:
    base, head = os.environ.get("PR_BASE"), os.environ.get("PR_HEAD", "")
    if not base:
        return "not a pull request; nothing to check"
    require(branch_problems(policy_for(root, base), base, head, os.environ.get("PR_SAME_REPO", "true") == "true"))
    return f"{head} -> {base} is allowed"


def requirement_text_changes(root: Path, base: str) -> list[str]:
    shown = run(["git", "show", f"origin/{base}:{REQS_PATH}"], root)
    if shown.returncode:
        return []
    frozen = ("document", "page", "level", "statement", "acceptance", "module")
    new = {r["id"]: r for r in load(root, REQS_PATH)["requirements"]}
    out = []
    for old in json.loads(shown.stdout)["requirements"]:
        if old["id"] not in new or any(old[k] != new[old["id"]][k] for k in frozen):
            out.append(f"requirement {old['id']} removed or reworded")
    return out


def check_protected_files(root: Path) -> str:
    base = os.environ.get("PR_BASE")
    policy = policy_for(root, base)
    manifest = root / policy["source_checksums"]
    problems = []
    for line in manifest.read_text(encoding="utf-8").split("\n"):
        if line.strip():
            digest, name = line.split()
            pdf = manifest.parent / name.lstrip("*")
            if pdf.exists() and hashlib.sha256(pdf.read_bytes()).hexdigest() != digest:
                problems.append(f"source document modified: {pdf.name}")
    if base and run(["git", "cat-file", "-e", f"origin/{base}:{POLICY_PATH}"], root).returncode == 0:
        changed = changed_files(root, base)
        if policy["source_checksums"] in changed:
            problems.append("source document checksums are immutable")
        touched = [f for f in changed if match_any(f, policy["protected_paths"])]
        touched += requirement_text_changes(root, base)
        touched += [f for f in changed if f.startswith(STATUS_DIR + "/") and (root / f).exists()
                    and load(root, f).get("status") == "done"]
        labels = os.environ.get("PR_LABELS", "").split(",")
        if touched and policy["protected_label"] not in labels:
            problems += [f"needs the '{policy['protected_label']}' label from a human: {f}" for f in touched]
    elif base:
        require(problems)
        return f"{base} has no policy yet (bootstrap); source checksums hold"
    require(problems)
    return "protected files unchanged or authorised"


def secrets_in(text: str) -> list[str]:
    return [p for p in SECRET_PATTERNS if re.search(p, text)]


def check_secret_scan(root: Path) -> str:
    files = repo_files(root)
    problems = []
    for f in files:
        name = f.rsplit("/", 1)[-1]
        if name == ".env" or (name.startswith(".env.") and name != ".env.example") or name.endswith((".pem", ".key")):
            problems.append(f"secret-bearing file committed: {f}")
        text = (root / f).read_bytes().decode("utf-8", errors="ignore")
        if secrets_in(text):
            problems.append(f"possible secret in {f}")
    env = root / ".env.example"
    if env.exists():
        problems += [f".env.example has a value: {line.split('=')[0]}" for line in env.read_text().splitlines()
                     if line and not line.startswith("#") and line.split("=", 1)[-1].strip()]
    require(problems)
    return f"{len(files)} files scanned"


def check_contract_tests(root: Path) -> str:
    from jsonschema import Draft202012Validator
    from openapi_spec_validator import validate as validate_openapi
    from referencing import Registry, Resource

    schema_dir = root / "contracts/schemas"
    schemas = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in schema_dir.glob("*.schema.json")}
    registry: Any = Registry().with_resources((n, Resource.from_contents(s)) for n, s in schemas.items())
    problems = []
    count = 0
    for name, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        stem = name.removesuffix(".schema.json")
        validator = Draft202012Validator(schema, registry=registry)
        valid = sorted((schema_dir / "examples").glob(f"{stem}.valid*.json"))
        invalid = sorted((schema_dir / "examples").glob(f"{stem}.invalid*.json"))
        if not valid or not invalid:
            problems.append(f"{name}: needs at least one valid and one invalid example")
        for ex in valid:
            problems += [f"{ex.name}: {e.message}" for e in validator.iter_errors(json.loads(ex.read_text("utf-8")))]
        problems += [f"{ex.name}: should be rejected" for ex in invalid
                     if validator.is_valid(json.loads(ex.read_text("utf-8")))]
        count += len(valid) + len(invalid)
    specs = list((root / "contracts/openapi").glob("*.json"))
    for spec in specs:
        try:
            validate_openapi(json.loads(spec.read_text(encoding="utf-8")), base_uri=spec.as_uri())
        except Exception as exc:  # any validator error is a failed contract
            problems.append(f"{spec.name}: {str(exc).splitlines()[0]}")
    config = load(root, "config/verdict.defaults.json")
    problems += [f"weights for {g} sum to {sum(w.values())}, not 100"
                 for g, w in config["weights"].items() if sum(w.values()) != 100]
    if not schemas or not specs:
        problems.append("no schemas or OpenAPI documents found")
    require(problems)
    return f"{len(schemas)} schemas, {count} examples, {len(specs)} OpenAPI documents"


def check_k8s_validate(root: Path) -> str:
    manifests = [f for f in repo_files(root) if f.startswith("k8s/") and f.endswith((".yaml", ".yml"))
                 and not f.endswith("kustomization.yaml")]
    if not manifests:
        raise Failure("no manifests under k8s/")
    problems = [f"{f}: image tag 'latest' is forbidden" for f in manifests
                if re.search(r"image:\s*\S+:latest\b", (root / f).read_text(encoding="utf-8"))]
    result = run([os.environ.get("KUBECONFORM", "kubeconform"), "-strict", "-summary", *manifests], root)
    if result.returncode:
        problems.append(result.stdout + result.stderr)
    require(problems)
    return result.stdout.strip()


def command(root: Path, args: list[str]) -> None:
    exe = args[0]
    if exe == "python":
        args = [sys.executable, *args[1:]]
    elif os.name == "nt" and exe == "npm":
        args = ["npm.cmd", *args[1:]]
    print("$", " ".join(args), flush=True)
    if subprocess.run(args, cwd=root).returncode:  # nosec B603
        raise Failure(f"command failed: {' '.join(args)}")


def check_gated(root: Path, name: str) -> str:
    """A check that applies once its code exists or its phase gate is passed. It never passes empty-handed."""
    policy = load(root, POLICY_PATH)
    rule = policy["gated_checks"][name]
    files = repo_files(root)
    implemented = [f for f in application_files(policy, files) if match_any(f, rule["triggers"])]
    implemented += [f for f in files if match_any(f, rule["triggers"]) and f.endswith((".py", ".json"))]
    due = rule["required_after"] in done_tasks(root)
    if not implemented and not due:
        return f"NOT APPLICABLE: no code under {rule['triggers'][0]} and gate {rule['required_after']} not passed"
    if not implemented:
        raise Failure(f"gate {rule['required_after']} is passed but nothing matches {rule['triggers']}")
    missing = [f for f in rule.get("must_exist", []) if not (root / f).is_file()]
    require([f"required file missing: {f}" for f in missing])
    if rule.get("builtin"):
        modules = sorted({"/".join(f.split("/")[:2]) for f in implemented if f.count("/") >= 2})
        require([f"{m} has code but no Dockerfile" for m in modules if not (root / m / "Dockerfile").is_file()])
        sha = git(root, "rev-parse", "--short", "HEAD")
        for m in modules:
            tag = f"{m.replace('/', '-')}:{sha}"
            command(root, ["docker", "build", "-t", tag, m])
            if rule["builtin"] == "image-scan":
                command(root, ["docker", "run", "--rm", "-v", "/var/run/docker.sock:/var/run/docker.sock",
                               policy["trivy_image"], "image", "--exit-code", "1", "--severity", "CRITICAL", tag])
        return f"{len(modules)} module images"
    for args in rule["commands"]:
        command(root, args)
    return "tests passed"


def check_lint(root: Path) -> str:
    command(root, ["python", "-m", "ruff", "check", "."])
    if any(f.startswith("services/ui/") and f.endswith((".ts", ".tsx")) for f in repo_files(root)):
        command(root, ["npm", "--prefix", "services/ui", "ci"])
        command(root, ["npm", "--prefix", "services/ui", "run", "lint"])
    return "ruff clean (and UI lint when UI code exists)"


def check_typecheck(root: Path) -> str:
    command(root, ["python", "-m", "mypy", "harness/verification", "--ignore-missing-imports"])
    files = repo_files(root)
    for top in ("services", "jobs"):
        if any(f.startswith(top + "/") and f.endswith(".py") for f in files):
            command(root, ["python", "-m", "mypy", top])
    if any(f.startswith("services/ui/") and f.endswith((".ts", ".tsx")) for f in files):
        command(root, ["npm", "--prefix", "services/ui", "ci"])
        command(root, ["npm", "--prefix", "services/ui", "run", "typecheck"])
    return "types check"


def check_harness_tests(root: Path) -> str:
    command(root, ["python", "-m", "unittest", "discover", "-s", "harness/tests", "-v"])
    return "harness tests passed"


def check_dependency_security(root: Path) -> str:
    command(root, ["python", "-m", "pip_audit", "-r", "requirements-dev.txt"])
    command(root, ["python", "-m", "bandit", "-q", "-r", "harness/verification", ".claude/hooks"])
    if (root / "services/ui/package-lock.json").exists():
        command(root, ["npm", "--prefix", "services/ui", "audit", "--audit-level=high"])
    return "dependency audit and static analysis clean"


def gate_problems(results: dict[str, str], expected: list[str]) -> list[str]:
    """Anything other than success, including skipped, blocks the merge."""
    wanted = [c for c in expected if c != "ci-gate"]
    return [f"{c}: {results.get(c, 'missing')}" for c in wanted if results.get(c) != "success"]


def check_ci_gate(root: Path) -> str:
    needs = json.loads(os.environ["NEEDS_JSON"])
    results = {k: v["result"] for k, v in needs.items()}
    require(gate_problems(results, list(results) or ["nothing"]))
    return "every required job succeeded"


CHECKS = {
    "repo-structure": check_repo_structure, "requirements-registry": check_requirements_registry,
    "traceability": check_traceability, "task-policy": check_task_policy,
    "branch-policy": check_branch_policy, "protected-files": check_protected_files,
    "secret-scan": check_secret_scan, "harness-tests": check_harness_tests, "lint": check_lint,
    "typecheck": check_typecheck, "contract-tests": check_contract_tests,
    "k8s-validate": check_k8s_validate, "dependency-security": check_dependency_security,
    "ci-gate": check_ci_gate,
}


def run_check(root: Path, name: str) -> bool:
    try:
        message = CHECKS[name](root) if name in CHECKS else check_gated(root, name)
    except Failure as exc:
        print(f"FAIL {name}\n{exc}")
        return False
    except Exception as exc:  # a crashing check is a failed check; the remaining checks still run
        print(f"FAIL {name}\n  - check crashed: {type(exc).__name__}: {exc}")
        return False
    print(f"PASS {name}: {message}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(f"**{name}**: {message}\n")
    return True


# ---------------------------------------------------------------- identity, claims, gh

def identity_problems(root: Path, policy: dict[str, Any]) -> tuple[str | None, list[str]]:
    email = git(root, "config", "user.email").lower()
    digest = hashlib.sha256(email.encode()).hexdigest()
    role = next((r for r, i in policy["identities"].items() if i["email_sha256"] == digest), None)
    if not role:
        return None, ["git user.email matches no registered contributor"]
    who, problems = policy["identities"][role], []
    if git(root, "config", "user.name") != who["git_name"]:
        problems.append(f"git user.name should be '{who['git_name']}'")
    if root.name.lower() != who["clone_dir"].lower():
        problems.append(f"{who['login']} must work in the '{who['clone_dir']}' clone, not '{root.name}'")
    helpers = git(root, "config", "--local", "--get-all", "credential.https://github.com.helper")
    if not re.search(rf"--user {re.escape(who['login'])}(?![\w-])", helpers):
        problems.append(f"clone credential helper is not pinned to {who['login']}")
    origin = git(root, "remote", "get-url", "origin").removesuffix(".git")
    if not origin.lower().endswith(policy["repository"].lower()):
        problems.append(f"wrong repository: {origin}")
    return role, problems


def identity(root: Path) -> tuple[str, dict[str, Any]]:
    policy = load(root, POLICY_PATH)
    role, problems = identity_problems(root, policy)
    require(problems)
    assert role  # nosec B101
    return role, policy["identities"][role]


def claim(root: Path, task_id: str) -> str:
    """Atomically create origin/claim/<task>; a second claim is rejected by git itself."""
    role, who = identity(root)
    git(root, "fetch", "-q", "origin")
    tasks = tasks_by_id(root, "origin/dev")
    if task_id not in tasks:
        raise Failure(f"unknown task {task_id}")
    if tasks[task_id]["owner"] != role:
        raise Failure(f"{task_id} is assigned to the {tasks[task_id]['owner']} contributor")
    states = task_states(root, "origin/dev")
    if task_id in states:
        raise Failure(f"{task_id} is already {states[task_id]}")
    require([f"blocked by {d}" for d in unmet_dependencies(tasks, task_id, states)])
    sha = git(root, "commit-tree", "origin/dev^{tree}", "-p", "origin/dev",
              "-m", f"claim {task_id} by {who['login']} {os.urandom(8).hex()}")
    ref = f"refs/heads/claim/{task_id}"
    pushed = run(["git", "push", f"--force-with-lease={ref}:", "origin", f"{sha}:{ref}"], root)
    if pushed.returncode:
        raise Failure(f"{task_id} is already claimed\n{pushed.stderr.strip()}")
    return f"claimed {task_id}; now: git switch -c feat/{task_id}-<name> origin/dev"


def gh(root: Path, args: list[str]) -> int:
    """Run gh as this clone's contributor without touching gh's shared active account."""
    decision, reason = command_decision(root, "scd.py gh -- " + " ".join(args))
    if decision == "deny":
        raise Failure(reason)
    _, who = identity(root)
    token = run(["gh", "auth", "token", "--hostname", "github.com", "--user", who["login"]]).stdout.strip()
    if not token:
        raise Failure(f"no gh login for {who['login']}")
    return subprocess.run(["gh", *args], env={**os.environ, "GH_TOKEN": token}).returncode  # nosec B603 B607


# ---------------------------------------------------------------- Claude Code hooks

SEGMENT = r"[^;&|\n]*"
PUSH = rf"\bgit\b{SEGMENT}\bpush\b{SEGMENT}"
API_WRITE = r"(-X\s*|--method[\s=]*)(POST|PUT|PATCH|DELETE)\b|\s(-f|-F|--field|--raw-field|--input)(\s|=)"
# Matched case-insensitively against the command with quotes removed.
DENY_COMMANDS = [
    (r"\bgh(\.exe)?\s+(pr|issue|api|release|label|workflow|run|repo|secret|ruleset)\b",
     "use 'python harness/verification/scd.py gh -- ...' so gh runs as this clone's contributor"),
    (r"\bgh(\.exe)?\s+auth\s+(switch|login|logout|refresh|setup-git)\b", "shared gh login must not change"),
    (PUSH + r"(\s--force\b|\s-(?-i:[a-eg-z]*f[a-z]*)\b|--force-with-lease|--mirror|--delete|\s-d\b|\s:\S|\s\+\S)",
     "force push and remote deletion are forbidden"),
    (PUSH + r"(\s|:|\+)(refs/heads/)?(main|dev)(?![\w./-])", "never push to main or dev"),
    (r"--no-verify|--no-gpg-sign", "do not bypass verification"),
    (rf"\bgit\b{SEGMENT}\bconfig\b{SEGMENT}(user\.(name|email)\s+\S|credential\.|core\.hookspath)",
     "identity configuration is fixed"),
    (rf"\bgit\b{SEGMENT}\s-c\s*(user\.(name|email)|credential\.|core\.hookspath)|\bGIT_(AUTHOR|COMMITTER)_(NAME|EMAIL)\b",
     "identity cannot be overridden per command"),
    (r"\b(switch|checkout)\b" + SEGMENT + r"\s(main|dev)(?![\w./-])[\s\S]*\bgit\b" + SEGMENT + r"\bcommit\b",
     "no direct commits on main or dev"),
    (rf"\bgh\s+--\s+api\b[\s\S]*({API_WRITE})|\bgh\s+--\s+api\b[\s\S]*\bmutation\b",
     "API writes (reviews, merges, labels, protection) are not available to sessions"),
    (r"(--label|--add-label|\s-l\s|/labels)[\s\S]*authorized-protected-change|"
     r"authorized-protected-change[\s\S]*(--label|--add-label|/labels)", "only a human adds the authorization label"),
    (r"\bpr\s+merge\b[\s\S]*--admin", "admin merge bypasses protection"),
    (r"\brepo\s+(edit|delete|rename|archive)\b", "repository settings need a human"),
    (r"SCD_HARNESS_MAINTENANCE", "only a human may enable harness maintenance"),
    (r"settings\.local\.json|disableAllHooks", "only a human may change local settings or hooks"),
]
PROTECTED_WRITE = (
    r"(>{1,2}|\btee\b|\bsed\b" + SEGMENT + r"\s-i|\b(Set|Add)-Content\b|\bOut-File\b|\b(Remove|Move|Copy)-Item\b|"
    r"\b(rm|mv|cp)\b)" + SEGMENT +
    r"(harness[/\\](verification|policies|tests|task-registry[/\\]tasks)|\.claude[/\\](settings|hooks)|"
    r"\.github[/\\](workflows|CODEOWNERS)|requirements-dev\.txt|pyproject\.toml|docs[/\\]source[/\\])")
ASK_COMMANDS = [
    (r"\bpr\s+review\b[\s\S]*(--approve\b|--request-changes\b|(?<!\S)-[ar](?!\S))",
     "a review decision belongs to the account owner"),
    (r"\bpr\s+merge\b", "merging needs confirmation"),
    (r"--add-label", "labels can carry authority"),
]


def command_decision(root: Path, line: str, maintenance: bool = False) -> tuple[str, str]:
    flat = re.sub(r"[\"'`]", "", line.replace("\\\n", " "))
    for pattern, reason in DENY_COMMANDS:
        if re.search(pattern, flat, re.I):
            return "deny", reason
    if not maintenance and re.search(PROTECTED_WRITE, flat, re.I):
        return "deny", "shell writes to protected files need maintenance mode, enabled by a human"
    if re.search(rf"\bgit\b{SEGMENT}\bcommit\b", flat):
        branch = git(root, "branch", "--show-current")
        if branch in load(root, POLICY_PATH)["branches"]["protected"]:
            return "deny", f"no direct commits on {branch}"
        _, problems = identity_problems(root, load(root, POLICY_PATH))
        if problems:
            return "deny", "; ".join(problems)
        if secrets_in(git(root, "diff", "--cached")) or secrets_in(git(root, "diff", "HEAD")):
            return "deny", "changes look like they contain a secret"
    for pattern, reason in ASK_COMMANDS:
        if re.search(pattern, flat, re.I):
            return "ask", reason
    return "allow", ""


def edit_decision(root: Path, path: str, content: str, maintenance: bool = False) -> tuple[str, str]:
    try:
        rel = Path(path).resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return "allow", ""  # outside the repository
    policy = load(root, POLICY_PATH)
    branch = git(root, "branch", "--show-current")
    if secrets_in(content):
        return "deny", "content looks like it contains a secret"
    if match_any(rel, policy["protected_paths"]) and not maintenance:
        return "deny", f"{rel} is protected; a human must start Claude with SCD_HARNESS_MAINTENANCE=1"
    if branch in policy["branches"]["protected"]:
        return "deny", f"do not edit on {branch}; claim a task and branch from origin/dev"
    if "P00" not in done_tasks(root) and application_files(policy, [rel]):
        return "deny", "Phase 0 forbids application implementation"
    found = re.match(policy["branches"]["task_pattern"], branch)
    if found:
        tasks = tasks_by_id(root)
        tid = found.group(2)
        if tid not in tasks:
            return "deny", f"branch names unknown task {tid}"
        unmet = unmet_dependencies(tasks, tid, task_states(root))
        if unmet:
            return "deny", f"{tid} is blocked by {', '.join(unmet)}"
        if not match_any(rel, tasks[tid]["allowed_paths"] + policy["always_allowed_paths"]):
            return "deny", f"{rel} is outside the scope of {tid}"
    return "allow", ""


def hook_decision(root: Path, event: dict[str, Any], maintenance: bool = False) -> tuple[str, str]:
    tool, data = event.get("tool_name", ""), event.get("tool_input", {})
    if tool in ("Bash", "PowerShell"):
        return command_decision(root, data.get("command", ""), maintenance)
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        content = json.dumps([data.get(k) for k in ("content", "new_string", "edits", "new_source")])
        return edit_decision(root, data.get("file_path") or data.get("notebook_path", ""), content, maintenance)
    if tool.startswith("mcp__") and re.search(r"repl|run_code|execute|shell", tool, re.I):
        return "ask", "this tool runs code that the harness cannot inspect"
    return "allow", ""


def hook(kind: str) -> int:
    event = json.loads(sys.stdin.read() or "{}")
    root = find_root(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd"))
    if kind == "pre-tool":
        decision, reason = hook_decision(root, event, os.environ.get("SCD_HARNESS_MAINTENANCE") == "1")
        if decision != "allow":
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse", "permissionDecision": decision,
                "permissionDecisionReason": f"SCD harness: {reason}"}}))
    elif kind == "session-start":
        role, problems = identity_problems(root, load(root, POLICY_PATH))
        who = load(root, POLICY_PATH)["identities"].get(role or "", {})
        print(f"SCD session: contributor={who.get('login', 'UNKNOWN')} branch={git(root, 'branch', '--show-current')}")
        print("Identity problems: " + "; ".join(problems) if problems else "Identity verified.")
        print(f"Read CLAUDE.md, Mandoff.md and {who.get('handoff', 'your handoff file')} before working.")
    elif kind == "stop":
        role, _ = identity_problems(root, load(root, POLICY_PATH))
        dirty = git(root, "status", "--porcelain")
        if role and dirty and load(root, POLICY_PATH)["identities"][role]["handoff"] not in dirty:
            print(json.dumps({"systemMessage": "SCD harness: uncommitted work and the handoff file is not updated."}))
    return 0


# ---------------------------------------------------------------- generated documents

def table(rows: list[list[str]]) -> str:
    head, *body = rows
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |" for row in body]
    return "\n".join(lines) + "\n"


def requirement_doc(title: str, reqs: list[dict[str, Any]]) -> str:
    out = [f"# {title}\n", f"Generated from `{REQS_PATH}`. Do not edit by hand. {len(reqs)} requirements.\n"]
    for module in sorted({r["module"] for r in reqs}, key=lambda m: (int(re.sub(r"\D", "", m)), m)):
        rows = [["ID", "Source", "Level", "Requirement", "Acceptance", "Verify by", "Status"]]
        rows += [[r["id"], f"{'Desc' if 'Desc' in r['document'] else 'Guide'} p{r['page']} §{r['section']}",
                  r["level"], r["statement"], r["acceptance"], r["verification"], r["status"]]
                 for r in reqs if r["module"] == module]
        out.append(f"## {module}\n\n{table(rows)}")
    return "\n".join(out)


def longest_path(tasks: dict[str, dict[str, Any]]) -> list[str]:
    memo: dict[str, tuple[int, list[str]]] = {}

    def best(tid: str) -> tuple[int, list[str]]:
        if tid not in memo:
            score, path = max((best(d) for d in tasks[tid]["depends_on"]), default=(0, []))
            memo[tid] = (score + tasks[tid]["points"], path + [tid])
        return memo[tid]

    return max(best(t) for t in tasks)[1]


def generated(root: Path) -> dict[str, str]:
    reqs = load(root, REQS_PATH)["requirements"]
    plan = load(root, TASKS_PATH)
    tasks = {t["id"]: t for t in plan["tasks"]}
    logins = {r: i["login"] for r, i in load(root, POLICY_PATH)["identities"].items()}
    done = done_tasks(root)
    functional = {"functional", "agent", "fine-tuning", "evaluation", "data"}
    docs = {
        "docs/requirements/Requirements.md": requirement_doc("Requirements specification", reqs),
        "docs/requirements/FunctionalRequirements.md": requirement_doc(
            "Functional, agent, data, model and evaluation requirements",
            [r for r in reqs if r["category"] in functional]),
        "docs/requirements/NonFunctionalRequirements.md": requirement_doc(
            "Non-functional, architecture, platform, security and process requirements",
            [r for r in reqs if r["category"] not in functional]),
    }
    rows = [["Requirement", "Source", "Module", "Phase", "Tasks", "Test", "Evidence", "Status"]]
    for r in reqs:
        ids = [t for t, v in tasks.items() if r["id"] in v["requirements"]]
        rows.append([r["id"], f"{r['document'].split('_')[-1][:-4]} p{r['page']}", r["module"],
                     ", ".join(sorted({f"P{tasks[t]['phase']:02d}" for t in ids})), ", ".join(ids),
                     r["verification"], ", ".join(r["evidence"]) or "none yet", r["status"]])
    docs["docs/requirements/RequirementsTraceabilityMatrix.md"] = (
        "# Requirements traceability matrix\n\nGenerated. Source requirement → module → phase → task → "
        "test → evidence.\n\n" + table(rows))
    out = ["# Implementation plan\n",
           f"Generated from `{TASKS_PATH}`. Phases after 0 are proposed and blocked until their gate dependencies "
           "are done and the decisions in `docs/requirements/PendingDecisions.md` that affect them are made.\n"]
    for phase in plan["phases"]:
        out.append(f"## {phase['id']}: {phase['title']}\n\nDemonstrable result: {phase['demonstration']}\n")
        for t in (v for v in plan["tasks"] if f"P{v['phase']:02d}" == phase["id"]):
            out.append(
                f"### {t['id']} {t['title']}\n\n{t['description']}\n\n"
                f"- Module {t['module']}; owner `{logins[t['owner']]}`; reviewer `{logins[t['reviewer']]}`; "
                f"complexity {t['complexity']}; status {'done' if t['id'] in done else 'not done'}\n"
                f"- Depends on: {', '.join(t['depends_on']) or 'nothing'}\n"
                f"- Requirements: {', '.join(t['requirements'])}\n"
                f"- File scope: {', '.join(f'`{p}`' for p in t['allowed_paths'])}\n"
                f"- Deliverables: {t['deliverables']}\n- Acceptance: {t['acceptance']}\n- Tests: {t['tests']}\n"
                f"- Verify: {'; '.join(f'`{c}`' for c in t['verification_commands'])}\n"
                f"- Evidence: {t['evidence']}\n- Needs: {', '.join(t['needs']) or 'nothing special'}\n"
                f"- Done when: {t['definition_of_done']}\n")
    docs["docs/planning/ImplementationPlan.md"] = "\n".join(out)
    path = longest_path(tasks)
    parallel = []
    for phase in plan["phases"][1:]:
        ids = [t for t, v in tasks.items() if "." in t and f"P{v['phase']:02d}" == phase["id"]]
        free = [t for t in ids if not set(tasks[t]["depends_on"]).intersection(ids)]
        parallel.append([phase["id"], ", ".join(free) or "none"])
    needs = [["Task", "Needs", "Title"]] + [[t, ", ".join(v["needs"]), v["title"]]
                                            for t, v in tasks.items() if v["needs"]]
    docs["docs/planning/CriticalPath.md"] = (
        "# Critical path and parallel work\n\nGenerated. Longest dependency chain by effort points "
        f"(S=1, M=3, L=5):\n\n`{' → '.join(path)}`\n\nTotal: {sum(tasks[t]['points'] for t in path)} points.\n\n"
        "## Tasks that can start together within a phase\n\n" + table([["Phase", "Parallel starters"], *parallel])
        + "\n## Tasks needing a human, credentials or a GPU\n\n" + table(needs))
    rows = [["Phase"] + [logins[r] for r in logins]]
    for phase in plan["phases"]:
        row = [phase["id"]]
        for role in logins:
            row.append(", ".join(t for t, v in tasks.items()
                                 if v["owner"] == role and f"P{v['phase']:02d}" == phase["id"]) or "-")
        rows.append(row)
    totals = [["Contributor", "Effort points", "Modules owned"]]
    for role, login in logins.items():
        mine = [v for v in tasks.values() if v["owner"] == role]
        totals.append([login, str(sum(v["points"] for v in mine)),
                       ", ".join(sorted({v["module"] for v in mine},
                                        key=lambda m: (int(re.sub(r"\D", "", m)), m)))])
    docs["docs/planning/TaskOwnership.md"] = (
        "# Task ownership\n\nGenerated. Proposed split (pending approval, decision D-08). Each pull request is "
        "reviewed by the other contributor. Effort points are estimates, not measured hours.\n\n"
        + table(totals) + "\n" + table(rows))
    graph = ["# Task dependency graph\n", "Generated.\n", "```mermaid", "flowchart LR"]
    for tid, t in tasks.items():
        graph += [f"  {d.replace('.', '_')}[{d}] --> {tid.replace('.', '_')}[{tid}]" for d in t["depends_on"]]
    docs["harness/task-registry/DependencyGraph.md"] = "\n".join([*graph, "```", ""])
    return docs


def render(root: Path, write: bool = True) -> list[str]:
    stale = []
    for rel, text in generated(root).items():
        target = root / rel
        text = text.rstrip("\n") + "\n"
        if not target.exists() or target.read_text(encoding="utf-8").replace("\r\n", "\n") != text:
            stale.append(rel)
            if write:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(text.encode("utf-8"))
    return stale


# ---------------------------------------------------------------- entry point

def main(argv: list[str]) -> int:
    usage = "usage: scd.py check <name>|all|render|identity|claim <task>|gh -- <args>|hook <kind>"
    if not argv:
        print(usage)
        return 2
    name, rest = argv[0], argv[1:]
    if name == "hook":
        try:
            return hook(rest[0])
        except Exception as exc:  # a broken guard must block, not wave actions through
            print(f"SCD harness hook failed: {exc}", file=sys.stderr)
            return 2 if rest[:1] == ["pre-tool"] else 1
    try:
        root = find_root()
        if name == "check":
            return 0 if run_check(root, rest[0]) else 1
        if name == "all":
            wanted = [c for c in load(root, POLICY_PATH)["required_checks"] if c != "ci-gate"]
            results = [(c, run_check(root, c)) for c in wanted]
            failed = [c for c, ok in results if not ok]
            print(f"\n{len(results) - len(failed)}/{len(results)} passed; failed: {', '.join(failed) or 'none'}")
            return 1 if failed else 0
        if name == "render":
            print("rewrote:", ", ".join(render(root)) or "nothing")
        elif name == "identity":
            role, who = identity(root)
            print(f"OK {role}: {who['login']} in {root.name}")
        elif name == "claim":
            print(claim(root, rest[0]))
        elif name == "gh":
            return gh(root, rest[1:] if rest[:1] == ["--"] else rest)
        else:
            print(usage)
            return 2
    except Failure as exc:
        print(f"FAIL {name}\n{exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
