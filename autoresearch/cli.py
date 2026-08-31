import argparse
import json
import subprocess
import sys
import urllib.error
from pathlib import Path
from typing import Any, Dict

from . import git_sync, markdown_index, ssh_runner, templates, zotero
from .config import ROOT, load_config, project_path


def print_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def format_error(exc: Exception) -> str:
    if isinstance(exc, subprocess.CalledProcessError):
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        detail = stderr or stdout
        if detail:
            return detail
    return str(exc)


def cmd_status(_args: argparse.Namespace) -> int:
    config = load_config()
    git = git_sync.status(ROOT)
    zotero_status: Dict[str, Any]
    try:
        zotero_status = zotero.ping(config)
    except Exception as exc:
        zotero_status = {"ok": False, "error": str(exc)}
    print_json(
        {
            "project": config["project"],
            "git": git,
            "zotero": zotero_status,
            "server_configured": bool(config["server"].get("ssh_target")),
        }
    )
    return 0


def cmd_zotero_ping(_args: argparse.Namespace) -> int:
    try:
        print_json(zotero.ping(load_config()))
        return 0
    except urllib.error.URLError as exc:
        print(f"Zotero Local API is not reachable: {exc}", file=sys.stderr)
        return 2


def cmd_zotero_sync(args: argparse.Namespace) -> int:
    config = load_config()
    output_dir = project_path("data", "zotero")
    result = zotero.sync(config, output_dir)
    print(f"Synced {result['count']} Zotero items.")
    for kind, path in result["paths"].items():
        print(f"{kind}: {path}")
    if args.checkpoint:
        return cmd_git_checkpoint(
            argparse.Namespace(message=args.message or "Sync Zotero library", no_push=False)
        )
    return 0


def cmd_notes_index(_args: argparse.Namespace) -> int:
    config = load_config()
    root = project_path(config["markdown"]["root"])
    output_path = project_path("data", "markdown-index.json")
    result = markdown_index.write_index(root, output_path)
    print(f"Indexed {result['count']} Markdown notes: {result['path']}")
    return 0


def cmd_idea_new(args: argparse.Namespace) -> int:
    config = load_config()
    path = project_path(config["markdown"]["idea_dir"])
    note = templates.create_idea(path, args.title, args.tags)
    print(f"Created idea note: {note}")
    if args.checkpoint:
        return cmd_git_checkpoint(
            argparse.Namespace(message=args.message or f"Add idea: {args.title}", no_push=False)
        )
    return 0


def cmd_remote_run(args: argparse.Namespace) -> int:
    result = ssh_runner.run_remote(load_config(), args.cmd, ROOT, timeout=args.timeout)
    print(result["stdout"], end="")
    if result["stderr"]:
        print(result["stderr"], file=sys.stderr, end="")
    return result["returncode"]


def cmd_experiment_run(args: argparse.Namespace) -> int:
    config = load_config()
    result = ssh_runner.run_remote(config, args.cmd, ROOT, timeout=args.timeout)
    experiment_dir = project_path(config["markdown"]["experiment_dir"])
    note = templates.create_experiment(
        experiment_dir,
        args.name,
        args.cmd,
        result["stdout"],
        result["stderr"],
        result["returncode"],
    )
    print(f"Recorded experiment: {note}")
    if result["returncode"] != 0:
        print(f"Remote command failed with return code {result['returncode']}", file=sys.stderr)
    if args.checkpoint:
        checkpoint_code = cmd_git_checkpoint(
            argparse.Namespace(
                message=args.message or f"Record experiment: {args.name}",
                no_push=False,
            )
        )
        if checkpoint_code != 0:
            return checkpoint_code
    return result["returncode"]


def cmd_git_checkpoint(args: argparse.Namespace) -> int:
    config = load_config()
    git_config = config["git"]
    push = bool(git_config.get("auto_push", True)) and not args.no_push
    try:
        result = git_sync.checkpoint(
            ROOT,
            args.message,
            branch=git_config.get("branch", "main"),
            remote=git_config.get("remote", "origin"),
            push=push,
        )
    except Exception as exc:
        print(f"Git checkpoint failed: {format_error(exc)}", file=sys.stderr)
        return 2
    print_json(result)
    return 0


def cmd_git_setup_remote(args: argparse.Namespace) -> int:
    config = load_config()
    git_config = config["git"]
    try:
        result = git_sync.setup_remote(
            ROOT,
            git_config.get("remote", "origin"),
            args.url,
            git_config.get("branch", "main"),
        )
    except Exception as exc:
        print(f"Git remote setup failed: {format_error(exc)}", file=sys.stderr)
        return 2
    print_json(result)
    return 0


def add_zotero_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("zotero")
    zotero_sub = parser.add_subparsers(dest="zotero_command", required=True)

    ping_parser = zotero_sub.add_parser("ping")
    ping_parser.set_defaults(func=cmd_zotero_ping)

    sync_parser = zotero_sub.add_parser("sync")
    sync_parser.add_argument("--checkpoint", action="store_true")
    sync_parser.add_argument("-m", "--message", default="")
    sync_parser.set_defaults(func=cmd_zotero_sync)


def add_notes_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("notes")
    notes_sub = parser.add_subparsers(dest="notes_command", required=True)

    index_parser = notes_sub.add_parser("index")
    index_parser.set_defaults(func=cmd_notes_index)


def add_idea_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("idea")
    idea_sub = parser.add_subparsers(dest="idea_command", required=True)

    new_parser = idea_sub.add_parser("new")
    new_parser.add_argument("--title", required=True)
    new_parser.add_argument("--tags", nargs="*", default=["idea"])
    new_parser.add_argument("--checkpoint", action="store_true")
    new_parser.add_argument("-m", "--message", default="")
    new_parser.set_defaults(func=cmd_idea_new)


def add_remote_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("remote")
    remote_sub = parser.add_subparsers(dest="remote_command", required=True)

    run_parser = remote_sub.add_parser("run")
    run_parser.add_argument("--cmd", required=True)
    run_parser.add_argument("--timeout", type=int, default=3600)
    run_parser.set_defaults(func=cmd_remote_run)


def add_experiment_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("experiment")
    exp_sub = parser.add_subparsers(dest="experiment_command", required=True)

    run_parser = exp_sub.add_parser("run")
    run_parser.add_argument("--name", required=True)
    run_parser.add_argument("--cmd", required=True)
    run_parser.add_argument("--timeout", type=int, default=3600)
    run_parser.add_argument("--checkpoint", action="store_true", default=True)
    run_parser.add_argument("--no-checkpoint", dest="checkpoint", action="store_false")
    run_parser.add_argument("-m", "--message", default="")
    run_parser.set_defaults(func=cmd_experiment_run)


def add_git_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("git")
    git_sub = parser.add_subparsers(dest="git_command", required=True)

    checkpoint_parser = git_sub.add_parser("checkpoint")
    checkpoint_parser.add_argument("-m", "--message", required=True)
    checkpoint_parser.add_argument("--no-push", action="store_true")
    checkpoint_parser.set_defaults(func=cmd_git_checkpoint)

    remote_parser = git_sub.add_parser("setup-remote")
    remote_parser.add_argument("--url", required=True)
    remote_parser.set_defaults(func=cmd_git_setup_remote)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="autoresearch")
    subparsers = parser.add_subparsers(dest="command", required=True)
    status_parser = subparsers.add_parser("status")
    status_parser.set_defaults(func=cmd_status)
    add_zotero_commands(subparsers)
    add_notes_commands(subparsers)
    add_idea_commands(subparsers)
    add_remote_commands(subparsers)
    add_experiment_commands(subparsers)
    add_git_commands(subparsers)
    return parser


def main(argv: Any = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
