from collections.abc import Iterable
import os
import re


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


def parse_commits(commits_str: str) -> list[str]:
    """Parse commits: handle both single-line and multiline formats.
    
    Cases:
    1. Multiple single-line commits (each line is a commit): 'feat: A\nfeat: B\nfeat: C'
    2. Multiline commits (commit + blank line + body): 'feat: A\n\nBREAKING CHANGE: ...\nfeat: B'
    3. Literal \\n from GitHub Actions env vars
    
    Returns list of commits where each may be multiline (subject + body).
    """
    if not commits_str:
        return []
    
    # Normalize: replace literal \n (from env vars) with actual newlines
    commits_str = commits_str.replace("\\n", "\n")
    
    # Strategy: look for Conventional Commits pattern at line start (type: or type():)
    # and group following lines (body) with the commit until next commit or end
    commits_list = []
    lines = commits_str.split('\n')
    current_commit = []
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check if this line starts a new conventional commit (type: or type():)
        if re.match(r'^[a-z]+(?:\([^)]*\))?(?:!)?:', line_stripped, re.I):
            # Save previous commit if exists
            if current_commit:
                commits_list.append('\n'.join(current_commit))
            # Start new commit
            current_commit = [line_stripped]
        elif current_commit:
            # Add to current commit's body (or skip empty lines)
            if line_stripped or current_commit[-1]:  # Include empty lines in body, but stop trailing
                current_commit.append(line_stripped)
        # else: skip leading empty lines before first commit
    
    # Add last commit
    if current_commit:
        commits_list.append('\n'.join(current_commit).strip())
    
    return [c for c in commits_list if c]


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

    # Join commits iterable into string if needed, then parse
    commits_str = "\n".join(commits) if isinstance(commits, list) else commits
    parsed_commits = parse_commits(commits_str)

    for commit_msg in parsed_commits:
        # Check for BREAKING CHANGE anywhere in the commit (subject or body)
        is_breaking = "BREAKING CHANGE" in commit_msg
        
        # Get first line (subject) for regex matching
        first_line = commit_msg.split("\n")[0]
        
        if m := re.match(r"^(?P<type>[a-z]+)(?:\([^)]*\))?(?P<bang>!)?:\s*(?P<desc>.+)$", first_line.strip(), re.I):
            desc = m["desc"].strip()
            # Check for breaking: either ! in commit or BREAKING CHANGE in body
            if m["bang"] or is_breaking:
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


def resolve_next_release_pure(raw_tags: str, changelog_text: str, commits: str) -> tuple[str, str]:
    """Pure function: deterministic, no I/O, no side effects.
    
    Args:
        raw_tags: Git tags output (one per line, sorted by -v:refname)
        changelog_text: Content of CHANGELOG.md
        commits: Commit messages (one per line, from git log --pretty=format:%s)
    
    Returns:
        Tuple of (version, release_notes)
    """
    latest_tag, tag_ver = find_latest_tag(raw_tags)
    changelog_ver = find_changelog_version(changelog_text)
    commit_list = [line.strip() for line in commits.splitlines() if line.strip()]
    
    return compute_release(max(tag_ver, changelog_ver), commit_list)


if __name__ == "__main__":
    raw_tags = os.environ.get("INPUT_RAW_TAGS", "")
    changelog_text = os.environ.get("INPUT_CHANGELOG_TEXT", "")
    commits = os.environ.get("INPUT_COMMITS", "")
    
    # Debug: log what we received
    import sys
    parsed = parse_commits(commits)
    print(f"DEBUG: received {len(commits)} chars, parsed {len(parsed)} commits", file=sys.stderr)
    for i, c in enumerate(parsed[:3]):
        print(f"  commit[{i}]: {c[:60]}...", file=sys.stderr)
    
    ver, notes = resolve_next_release_pure(raw_tags, changelog_text, commits)
    
    # Create output object
    output = {
        "version": ver,
        "release_notes": notes
    }
    
    # Prepare JSON output
    json_str = json.dumps(output, ensure_ascii=False)
    
    # Write to GITHUB_OUTPUT
    if gh_out := os.environ.get("GITHUB_OUTPUT"):
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"json_output={json_str}\n")
