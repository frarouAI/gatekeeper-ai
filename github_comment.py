"""
GitHub PR Commenter for Gatekeeper.

- Reads .gatekeeper/ci-summary.json
- Posts or updates a single PR comment
- Never fails CI
"""

import json
import os
import sys
import urllib.request
import urllib.error

GATEKEEPER_MARKER = "<!-- gatekeeper-ci -->"


def _github_api_request(method, url, token, data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    if data:
        req.add_header("Content-Type", "application/json")
        data = json.dumps(data).encode("utf-8")
    return urllib.request.urlopen(req, data=data, timeout=10)


def load_summary(path=".gatekeeper/ci-summary.json"):
    with open(path, "r") as f:
        return json.load(f)


def build_comment(summary):
    status = "✅ PASSED" if summary["ci_pass"] else "❌ FAILED"

    return f"""{GATEKEEPER_MARKER}
### 🛡️ Gatekeeper CI — {status}

**Files checked:** {summary["files_checked"]}  
**Compliant:** {summary["compliant_files"]}  
**Non-compliant:** {summary["non_compliant_files"]}  
**Quality score:** {summary["team_quality_score"]:.2f}

**Owner policy:** `{summary["owner_policy"]["mode"]}`  
Unowned files: {summary["owner_policy"]["total_unowned_files"]}

<sub>Gatekeeper CI · deterministic · artifact-driven</sub>
"""


def main():
    token = os.getenv("GITHUB_TOKEN")
    event_path = os.getenv("GITHUB_EVENT_PATH")
    repo = os.getenv("GITHUB_REPOSITORY")

    if not token or not event_path or not repo:
        print("ℹ️ GitHub context missing — skipping PR comment")
        return

    with open(event_path, "r") as f:
        event = json.load(f)

    pr = event.get("pull_request")
    if not pr:
        print("ℹ️ Not a pull request — skipping PR comment")
        return

    issue_url = pr["comments_url"]

    try:
        summary = load_summary()
        body = build_comment(summary)

        # Fetch existing comments
        resp = _github_api_request("GET", issue_url, token)
        comments = json.loads(resp.read().decode("utf-8"))

        for c in comments:
            if GATEKEEPER_MARKER in c.get("body", ""):
                _github_api_request(
                    "PATCH",
                    c["url"],
                    token,
                    {"body": body},
                )
                print("✅ Gatekeeper PR comment updated")
                return

        # Create new comment
        _github_api_request(
            "POST",
            issue_url,
            token,
            {"body": body},
        )
        print("✅ Gatekeeper PR comment created")

    except Exception as exc:
        print(f"⚠️ GitHub comment failed: {type(exc).__name__}: {exc}")
        print("⚠️ CI continues")


if __name__ == "__main__":
    main()
