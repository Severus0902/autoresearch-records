from datetime import datetime
from pathlib import Path
from typing import Iterable, List


def slugify(value: str) -> str:
    chars: List[str] = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        elif char in {" ", "-", "_"}:
            chars.append("-")
    slug = "".join(chars).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "note"


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def frontmatter(title: str, note_type: str, status: str, tags: Iterable[str]) -> str:
    tag_list = ", ".join(f'"{tag}"' for tag in tags)
    return "\n".join(
        [
            "---",
            f'title: "{title}"',
            f"type: {note_type}",
            f"status: {status}",
            f'created: "{iso_now()}"',
            "zotero: []",
            f"tags: [{tag_list}]",
            "---",
            "",
        ]
    )


def create_idea(path: Path, title: str, tags: Iterable[str]) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    note_path = path / f"{now_stamp()}-{slugify(title)}.md"
    content = frontmatter(title, "idea", "open", tags)
    content += f"# {title}\n\n## Question\n\n## Hypothesis\n\n## Related Literature\n\n## Next Action\n"
    note_path.write_text(content, encoding="utf-8")
    return note_path


def create_experiment(path: Path, name: str, command: str, output: str, error: str, returncode: int) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    note_path = path / f"{now_stamp()}-{slugify(name)}.md"
    status = "done" if returncode == 0 else "failed"
    content = frontmatter(name, "experiment", status, ["experiment"])
    content += f"# {name}\n\n"
    content += "## Command\n\n"
    content += f"```bash\n{command}\n```\n\n"
    content += "## Result\n\n"
    content += f"Return code: `{returncode}`\n\n"
    content += "## Stdout\n\n"
    content += f"```text\n{output.rstrip()}\n```\n\n"
    content += "## Stderr\n\n"
    content += f"```text\n{error.rstrip()}\n```\n\n"
    content += "## Interpretation\n\n"
    note_path.write_text(content, encoding="utf-8")
    return note_path

