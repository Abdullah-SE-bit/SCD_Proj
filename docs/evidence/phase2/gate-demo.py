"""P02 demonstration through the cluster's ingress. usage: p02-demo.py BASE CONTEXT

Prints every request and answer; the token is never printed. Account and ideas are invented for the run.
"""

import json
import secrets
import subprocess
import sys
import urllib.error
import urllib.request

base, context = sys.argv[1], sys.argv[2]
token = ""


def call(method, path, body=None, signed=False, show=True):
    headers = {"Content-Type": "application/json"} | ({"Authorization": f"Bearer {token}"} if signed else {})
    request = urllib.request.Request(base + path, method=method, headers=headers,
                                     data=None if body is None else json.dumps(body).encode())
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status, answer = response.status, json.load(response)
    except urllib.error.HTTPError as error:
        status, answer = error.code, json.load(error)
    if show:
        shown = {k: ("<not recorded>" if k == "password" else v) for k, v in body.items()} if body else None
        print(f"{method} {path}{' (signed in)' if signed else ''}" + (f" {json.dumps(shown)}" if shown else ""))
        print(f"  {status} {json.dumps(answer)[:700]}")
    return status, answer


email = f"gate-{secrets.token_hex(4)}@example.org"
login = {"email": email, "password": secrets.token_urlsafe(18)}
print("## Register and log in")
status, account = call("POST", "/api/auth/register", login)
assert status == 201
assert call("POST", "/api/auth/login", login | {"password": "not the password"})[0] == 401
status, answer = call("POST", "/api/auth/login", login, show=False)
assert status == 200
token = answer["token"]
print("POST /api/auth/login (correct password)\n  200 a token was returned (not recorded)")

print("\n## Edit the profile")
assert call("GET", "/api/profile")[0] == 401
assert call("GET", "/api/profile", signed=True)[0] == 404
profile = {"skills": ["python"], "hours_per_week": 10, "weeks_available": 12, "team_size": 2, "compute": "laptop",
           "goal": "portfolio", "interests": ["education"]}
assert call("PUT", "/api/profile", profile, signed=True)[1]["version"] == 1
edited = profile | {"hours_per_week": 6, "goal": "course_project"}
assert call("PUT", "/api/profile", edited, signed=True)[1]["version"] == 2
status, saved = call("GET", "/api/profile", signed=True)
assert (saved["hours_per_week"], saved["goal"], saved["version"]) == (6.0, "course_project", 2)

print("\n## History of a new account, as the product gives it")
assert call("GET", "/api/ideas", signed=True) == (200, {"ideas": []})
status, run = call("POST", "/api/validate", {"idea": "Study planner for lab groups"}, show=False)
print(f"POST /api/validate  {status} {json.dumps(run)}")
assert call("GET", "/api/ideas", signed=True) == (200, {"ideas": []})
print("# No public route saves an idea yet (the Validate flow is P05), so checking one leaves history empty.")

print("\n## History with records written directly to the profile service (not a user action)")
verdict = json.load(open("contracts/schemas/examples/verdict.valid.json", encoding="utf-8"))
seed = """
import json, sys, urllib.request
user, verdict = sys.argv[1], json.load(sys.stdin)
def post(path, body):
    request = urllib.request.Request("http://127.0.0.1:8000" + path, data=json.dumps(body).encode(), method="POST")
    return json.load(urllib.request.urlopen(request, timeout=10))
first = post(f"/users/{user}/ideas",
             {"title": "Seeded idea A", "text": "SEEDED DEMO RECORD: first version", "source": "own"})
post(f"/users/{user}/ideas/{first['idea_id']}/versions", {"text": "SEEDED DEMO RECORD: second version"})
post(f"/users/{user}/ideas/{first['idea_id']}/versions/2/verdict", verdict)
post(f"/users/{user}/ideas", {"title": "Seeded idea B", "text": "SEEDED DEMO RECORD: other idea", "source": "own"})
print("seeded 2 ideas, 3 versions, 1 verdict (the contract example)")
"""
done = subprocess.run(["kubectl", "--context", context, "-n", "idea-validator", "exec", "-i", "deploy/profile", "--",
                       "python", "-c", seed, account["user_id"]], input=json.dumps(verdict), text=True,
                      capture_output=True, check=True)
print("kubectl exec deploy/profile: " + done.stdout.strip())
status, history = call("GET", "/api/ideas", signed=True)
ids = [idea["idea_id"] for idea in history["ideas"]]
assert len(ids) == 2
assert len(call("GET", f"/api/ideas/{ids[0]}/versions", signed=True)[1]["versions"]) == 2
assert call("GET", f"/api/compare?a={ids[0]}&b={ids[1]}", signed=True)[0] == 200
assert call("GET", f"/api/ideas/{ids[0]}/versions")[0] == 401
print("\nAll assertions of this script passed.")
