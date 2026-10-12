#!/usr/bin/env python3
"""Poll GitHub for Dependabot PRs ready for staging deployment."""

import json
import logging
import os
import subprocess
import time
import urllib.error
import urllib.request

REPO = "mpresswala/cricbox"
WORK_DIR = "/root/cricbox"
STATE_FILE = "/var/lib/cricbot/deployed.json"
LOG_FILE = "/var/log/cricbot.log"
STAGING_SERVICE = "cricbox-staging"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
log = logging.getLogger("cricbot")


def api_get(path):
    url = "https://api.github.com/repos/%s/%s" % (REPO, path)
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "cricbot",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        log.warning("API %s -> %s", url, e.code)
        return None


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"deployed": []}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def all_checks_pass(sha):
    """Check that ALL completed CI checks passed for a commit."""
    data = api_get("commits/%s/check-runs" % sha)
    if not data:
        return False
    for cr in data.get("check_runs", []):
        if cr["status"] == "completed" and cr["conclusion"] != "success":
            if cr["name"] != "Dependabot":
                log.info(
                    "Check '%s' failed (%s)", cr["name"], cr["conclusion"]
                )
                return False
    return True


def run_cmd(cmd, cwd=None, timeout=120):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=timeout,
    )
    if result.returncode != 0:
        log.warning("exit=%d: %s", result.returncode, cmd[:120])
    return result.returncode, result.stdout, result.stderr


def deploy_pr(pr_number, branch, sha):
    log.info("=== Deploying PR #%s (%s) ===", pr_number, branch)

    ret, _, _ = run_cmd(
        "git fetch origin pull/%s/head:deploy-pr-%s" % (pr_number, pr_number),
        cwd=WORK_DIR,
        timeout=30,
    )
    if ret != 0:
        return False
    run_cmd("git checkout deploy-pr-%s" % pr_number, cwd=WORK_DIR, timeout=15)

    ret, _, _ = run_cmd(
        "cd %s && uv sync --frozen 2>&1" % WORK_DIR, timeout=180
    )
    if ret != 0:
        run_cmd("git checkout main", cwd=WORK_DIR)
        run_cmd("git branch -D deploy-pr-%s" % pr_number, cwd=WORK_DIR)
        return False

    ret, _, _ = run_cmd(
        "cd %s && DJANGO_SECRET_KEY=ci-test-key-not-used-in-production "
        "DJANGO_SETTINGS_MODULE=cricbox.settings_staging "
        "uv run python cricbox/manage.py test "
        "batsman bowler home match match_statistics opposition player venue "
        "--verbosity=1 2>&1" % WORK_DIR,
        timeout=180,
    )
    if ret != 0:
        log.error("Tests failed for PR #%s", pr_number)
        run_cmd("git checkout main", cwd=WORK_DIR)
        run_cmd("git branch -D deploy-pr-%s" % pr_number, cwd=WORK_DIR)
        return False
    log.info("Tests passed for PR #%s", pr_number)

    run_cmd(
        "cd %s && DJANGO_SECRET_KEY=staging-validation-key "
        "DJANGO_SETTINGS_MODULE=cricbox.settings_staging "
        "uv run python cricbox/manage.py migrate 2>&1" % WORK_DIR,
        timeout=60,
    )
    run_cmd(
        "cd %s && DJANGO_SECRET_KEY=staging-validation-key "
        "DJANGO_SETTINGS_MODULE=cricbox.settings_staging "
        "uv run python cricbox/manage.py collectstatic --no-input 2>&1"
        % WORK_DIR,
        timeout=60,
    )

    ret, _, _ = run_cmd(
        "systemctl restart %s" % STAGING_SERVICE, timeout=30
    )
    if ret != 0:
        log.error("Failed to restart staging")
        run_cmd("git checkout main", cwd=WORK_DIR)
        return False

    time.sleep(3)
    ret, out, _ = run_cmd(
        "curl -s -o /dev/null -w '%%{http_code}' http://localhost:8000/",
        timeout=10,
    )
    status = out.strip()
    log.info("PR #%s deployed (HTTP %s)", pr_number, status)

    run_cmd("git checkout main", cwd=WORK_DIR)
    run_cmd("git branch -D deploy-pr-%s" % pr_number, cwd=WORK_DIR)
    return True


def main():
    state = load_state()
    deployed = set(state["deployed"])
    log.info("Checking for Dependabot PRs...")
    pulls = api_get("pulls?state=open&per_page=10")
    if not pulls:
        return
    for pr in pulls:
        number = pr["number"]
        if number in deployed:
            continue
        if pr["user"]["login"] != "dependabot[bot]":
            continue
        sha = pr["head"]["sha"]
        title = pr["title"]
        log.info("Found PR #%s: %s", number, title)
        if not all_checks_pass(sha):
            log.info(
                "PR #%s checks not all passing, skipping", number
            )
            continue
        log.info("PR #%s checks passed, deploying...", number)
        if deploy_pr(number, pr["head"]["ref"], sha):
            deployed.add(number)
            state["deployed"] = sorted(deployed)
            save_state(state)
            log.info("PR #%s deployed: %s", number, title)
        else:
            log.error("PR #%s deployment failed", number)


if __name__ == "__main__":
    main()
