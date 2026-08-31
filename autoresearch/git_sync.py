import subprocess
from pathlib import Path
from typing import Dict, List, Optional


def run_git(args: List[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=check,
    )


def is_git_repo(cwd: Path) -> bool:
    result = run_git(["rev-parse", "--is-inside-work-tree"], cwd, check=False)
    return result.returncode == 0 and result.stdout.strip() == "true"


def ensure_git_repo(cwd: Path, branch: str) -> None:
    if not is_git_repo(cwd):
        run_git(["init"], cwd)
    current = run_git(["branch", "--show-current"], cwd, check=False).stdout.strip()
    if not current:
        return
    if current != branch:
        run_git(["branch", "-M", branch], cwd)


def has_changes(cwd: Path) -> bool:
    result = run_git(["status", "--porcelain"], cwd)
    return bool(result.stdout.strip())


def remote_exists(cwd: Path, remote: str) -> bool:
    result = run_git(["remote"], cwd)
    return remote in result.stdout.split()


def setup_remote(cwd: Path, remote: str, url: str, branch: str) -> Dict[str, str]:
    ensure_git_repo(cwd, branch)
    if remote_exists(cwd, remote):
        run_git(["remote", "set-url", remote, url], cwd)
        action = "updated"
    else:
        run_git(["remote", "add", remote, url], cwd)
        action = "added"
    run_git(["branch", "-M", branch], cwd)
    return {"remote": remote, "url": url, "branch": branch, "action": action}


def checkpoint(
    cwd: Path,
    message: str,
    branch: str = "main",
    remote: str = "origin",
    push: bool = True,
) -> Dict[str, Optional[str]]:
    ensure_git_repo(cwd, branch)
    if not has_changes(cwd):
        return {"committed": "false", "pushed": "false", "commit": None}

    if push and not remote_exists(cwd, remote):
        return {
            "committed": "false",
            "pushed": "false",
            "commit": None,
            "warning": f"Remote '{remote}' is not configured. Add a GitHub remote before checkpointing.",
        }

    run_git(["add", "-A"], cwd)
    run_git(["commit", "-m", message], cwd)
    commit = run_git(["rev-parse", "--short", "HEAD"], cwd).stdout.strip()

    pushed = "false"
    if push:
        run_git(["push", "-u", remote, branch], cwd)
        pushed = "true"

    return {"committed": "true", "pushed": pushed, "commit": commit}


def status(cwd: Path) -> Dict[str, str]:
    if not is_git_repo(cwd):
        return {"repo": "false", "branch": "", "changes": ""}
    branch = run_git(["branch", "--show-current"], cwd, check=False).stdout.strip()
    changes = run_git(["status", "--short"], cwd).stdout.strip()
    return {
        "repo": "true",
        "branch": branch,
        "changes": changes,
    }
