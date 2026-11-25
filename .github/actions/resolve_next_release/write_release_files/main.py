from datetime import date
from pathlib import Path
import os
import re

DEFAULT_CHANGELOG_HEADER = (
    "# Changelog\n\n"
    "All notable changes to this project will be documented in this file.\n\n"
    "The format is based on [Keep a Changelog](https://keepachangelog.com),\n"
    "and this project adheres to [Semantic Versioning](https://semver.org).\n"
)


def render_updated_changelog(
    existing_content: str,
    version: str,
    release_notes: str,
    release_date: str,
) -> str:
    content = existing_content if existing_content.strip() else DEFAULT_CHANGELOG_HEADER
    release_block = f"## [{version}] - {release_date}\n\n{release_notes}"

    if m_ver := re.search(r"^## \[(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)\]", content, re.M):
        return content[:m_ver.start()] + release_block + "\n\n" + content[m_ver.start():]

    return content.rstrip() + "\n\n" + release_block + "\n"


def write_release_files(repo_dir: Path, version: str, release_notes: str, release_date: str) -> None:
    (repo_dir / "VERSION").write_text(f"{version}\n", encoding="utf-8")

    changelog_path = repo_dir / "CHANGELOG.md"
    if changelog_path.is_file():
        raw_bytes = changelog_path.read_bytes()
        is_crlf = b"\r\n" in raw_bytes
        content = raw_bytes.decode("utf-8", errors="replace").replace("\r\n", "\n")
    else:
        is_crlf = False
        content = DEFAULT_CHANGELOG_HEADER

    updated = render_updated_changelog(content, version, release_notes, release_date)
    if is_crlf:
        updated = updated.replace("\n", "\r\n")

    changelog_path.write_bytes(updated.encode("utf-8"))


if __name__ == "__main__":
    write_release_files(
        repo_dir=Path.cwd(),
        version=os.environ["RELEASE_VERSION"].strip(),
        release_notes=os.environ["RELEASE_NOTES"].strip(),
        release_date=date.today().isoformat(),
    )
