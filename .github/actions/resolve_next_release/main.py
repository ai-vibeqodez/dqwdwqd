from collections.abc import Iterable
from pathlib import Path
import os
import re
import subprocess


def parse_semver(raw: str) -> tuple[int, int, int] | None:
    if m := re.match(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$", raw.strip()):
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return None


def find_latest_tag(raw_tags: str) -> tuple[str | None, tuple[int, int, int]]:
    for line in raw_tags.splitlines():
        tag = line.strip()
        if tag.startswith("v") and (parsed := parse_semver(tag.removeprefix("v"))):
            return tag, parsed
    return None, (0, 0, 0)


def find_changelog_version(changelog_text: str) -> tuple[int, int, int]:
    for line in changelog_text.splitlines():
        if m := re.match(r"^## \[([^\]]+)\]", line):
            if parsed := parse_semver(m.group(1)):
                return parsed
    return 0, 0, 0


def compute_release(
    base_version: tuple[int, int, int],
    commits: Iterable[str],
) -> tuple[str, str]:
    major, minor, patch = base_version
    type_map = {
        "feat": "Added",
        "fix": "Fixed",
        "refactor": "Changed",
        "perf": "Changed",
        "deprecate": "Deprecated",
        "remove": "Removed",
        "revert": "Removed",
        "security": "Security",
    }
    sections: dict[str, list[str]] = {
        k: [] for k in ("Breaking", "Added", "Changed", "Deprecated", "Removed", "Fixed", "Security")
    }

    for line in commits:
        if m := re.match(r"^(?P<type>[a-z]+)(?:\([^)]*\))?(?P<bang>!)?:\s*(?P<desc>.+)$", line.strip(), re.I):
            desc = m["desc"].strip()
            if m["bang"] or "BREAKING CHANGE" in line:
                sections["Breaking"].append(desc)
            elif cat := type_map.get(m["type"].lower()):
                sections[cat].append(desc)

    if not any(sections.values()):
        sections["Changed"].append("Maintenance release")

    if sections["Breaking"]:
        next_version = f"{major + 1}.0.0"
    elif sections["Added"]:
        next_version = f"{major}.{minor + 1}.0"
    else:
        next_version = f"{major}.{minor}.{patch + 1}"

    release_notes = "\n\n".join(
        f"### {cat}\n\n" + "\n".join(f"- {i}" for i in items)
        for cat, items in sections.items()
        if items
    )
    return next_version, release_notes


def run_git(*args: str, repo_dir: Path) -> str:
    res = subprocess.run(["git", *args], cwd=repo_dir, capture_output=True, text=True)
    return res.stdout if res.returncode == 0 else ""


def resolve_next_release(repo_dir: Path) -> tuple[str, str]:
    raw_tags = run_git("tag", "--merged", "HEAD", "--sort=-v:refname", repo_dir=repo_dir)
    latest_tag, tag_ver = find_latest_tag(raw_tags)

    changelog_path = repo_dir / "CHANGELOG.md"
    changelog_ver = (
        find_changelog_version(changelog_path.read_text(encoding="utf-8", errors="replace"))
        if changelog_path.is_file()
        else (0, 0, 0)
    )

    rev_range = f"{latest_tag}..HEAD" if latest_tag else "HEAD"
    commits = run_git("log", rev_range, "--no-merges", "--pretty=format:%s", repo_dir=repo_dir).splitlines()

    return compute_release(max(tag_ver, changelog_ver), commits)


if __name__ == "__main__":
    ver, notes = resolve_next_release(Path.cwd())
    if gh_out := os.environ.get("GITHUB_OUTPUT"):
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"version={ver}\n")
            f.write(f"release_notes<<EOF\n{notes}\nEOF\n")
