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
    """Pure function: renders updated CHANGELOG content.
    
    Args:
        existing_content: Existing CHANGELOG.md content (normalized to LF)
        version: Version string (e.g. "1.2.3")
        release_notes: Formatted release notes with sections
        release_date: Date in YYYY-MM-DD format
    
    Returns:
        Updated CHANGELOG content (with new release prepended)
    """
    content = existing_content if existing_content.strip() else DEFAULT_CHANGELOG_HEADER
    release_block = f"## [{version}] - {release_date}\n\n{release_notes}"

    # Find first existing release and insert before it
    if m_ver := re.search(r"^## \[(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)\]", content, re.M):
        return content[:m_ver.start()] + release_block + "\n\n" + content[m_ver.start():]

    # No existing releases: append at end
    return content.rstrip() + "\n\n" + release_block + "\n"


def apply_line_ending(content: str, preserve_crlf: bool) -> str:
    """Convert line endings if needed.
    
    Args:
        content: Content with LF line endings
        preserve_crlf: If True, convert LF to CRLF
    
    Returns:
        Content with appropriate line endings
    """
    if preserve_crlf:
        return content.replace("\n", "\r\n")
    return content


if __name__ == "__main__":
    import sys
    
    existing_changelog = os.environ.get("INPUT_EXISTING_CHANGELOG", "")
    version = os.environ.get("INPUT_VERSION", "").strip()
    release_notes = os.environ.get("INPUT_RELEASE_NOTES", "").strip()
    release_date = os.environ.get("INPUT_RELEASE_DATE", "").strip()
    preserve_crlf = os.environ.get("INPUT_PRESERVE_CRLF", "false").lower() == "true"

    # Normalize input: replace literal \n with actual newlines
    existing_changelog = existing_changelog.replace("\\n", "\n")
    release_notes = release_notes.replace("\\n", "\n")

    # Render changelog (pure computation, no side effects)
    updated_changelog = render_updated_changelog(
        existing_changelog,
        version,
        release_notes,
        release_date,
    )

    # Apply line endings
    changelog_output = apply_line_ending(updated_changelog, preserve_crlf)
    version_output = apply_line_ending(f"{version}\n", preserve_crlf)

    # Output to stdout (pure function output, no file writes)
    # JSON format for safe multiline handling
    import json
    output = {
        "version": version_output.strip(),
        "changelog": changelog_output
    }
    print(json.dumps(output, ensure_ascii=False), flush=True)
