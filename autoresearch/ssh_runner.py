import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List


def build_remote_command(command: str, remote_workdir: str) -> str:
    if remote_workdir:
        return f"cd {shlex.quote(remote_workdir)} && {command}"
    return command


def run_remote(config: Dict[str, Any], command: str, cwd: Path, timeout: int = 3600) -> Dict[str, Any]:
    server = config["server"]
    target = server.get("ssh_target", "")
    if not target:
        raise RuntimeError("server.ssh_target is empty. Fill it in config.local.json.")

    ssh_options: List[str] = list(server.get("ssh_options", []))
    remote_command = build_remote_command(command, server.get("remote_workdir", ""))
    args = ["ssh"] + ssh_options + [target, remote_command]
    result = subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "command": command,
        "target": target,
    }

