# AGENTS.md — Architecture & Patterns

## Pure vs IO Architecture

### Concept
Separation of components into two categories for better testability and maintainability:

**Pure components** — deterministic functions without side effects
- Input: strings and structured data
- Output: computed result
- Guarantee: same inputs → always identical output
- Zero side effects, zero environment dependencies

**IO components** — environment interaction
- Read files (git tags, CHANGELOG.md, VERSION)
- Execute commands (git log, git describe, date)
- Write files and determine state (line endings, date)
- Call pure components with gathered data

### Project Examples

#### release__resolve_next_release_pure
Pure function for versioning:
```python
def resolve_next_release_pure(raw_tags: str, changelog_text: str, commits: str) -> tuple[str, str]:
    # Parse tags: "v1.2.3\nv1.0.0" → (1, 2, 3)
    # Parse CHANGELOG: search ## [X.Y.Z]
    # Analyze commits: conventional commits by types
    # Return: (version, release_notes)
    # 100% deterministic
```

#### release__resolve_next_release_io
IO layer:
```bash
# Gather data:
RAW_TAGS=$(git tag --merged HEAD --sort=-v:refname)
CHANGELOG_TEXT=$(cat CHANGELOG.md || echo "")
COMMITS=$(git log ... --pretty=format:%s)

# Call pure:
uses: ./.github/actions/release__resolve_next_release_pure@main
with:
  raw_tags: $RAW_TAGS
  changelog_text: $CHANGELOG_TEXT
  commits: $COMMITS
```

---

## Naming Convention

### Pattern
```
{domain}__{name}_{suffix}
```

Suffixes at the end (not in the middle):
- `_pure` — deterministic function
- `_io` — I/O layer

### Examples ✓
- `release__resolve_next_release_pure`
- `release__resolve_next_release_io`
- `release__write_release_files_pure`
- `release__write_release_files_io`
- `test__resolve_next_release_pure`
- `test__write_release_files_pure`

### Anti-examples ✗
- ~~`release__pure_resolve_next_release`~~ (io/pure in the middle)
- ~~`release__io_write_release_files`~~ (io/pure in the middle)

---

## GitHub Actions Patterns

### Input Handling

#### Multiline inputs
GitHub Actions escapes `\n` as literal two characters `\` + `n`:
```yaml
with:
  release_notes: |
    ### Added
    - Feature A
    - Feature B
```

Arrives in env as:
```
INPUT_RELEASE_NOTES: ### Added\n- Feature A\n- Feature B
```

**Solution:** normalize in Python/Bash:
```python
release_notes = os.environ.get("INPUT_RELEASE_NOTES", "")
release_notes = release_notes.replace("\\n", "\n")  # Now real newlines
```

#### Backticks in bash
Backticks `` ` `` are interpreted as command substitution in bash and cause errors:
```bash
# ❌ Bad: `code` → attempt to execute "code" command
echo "$content" | grep -q "Support for `code`" || exit 1
# Error: code: command not found
```

**Solution 1:** heredoc with single quotes (doesn't interpret special chars):
```bash
cat > /tmp/script.sh << 'EOF'
content="${{ steps.test.outputs.content }}"
grep -q "Support for" "$content" || exit 1  # Backticks will be as-is in file
EOF
bash /tmp/script.sh
```

**Solution 2:** check other parts of string:
```bash
echo "$content" | grep -q "Support for" || exit 1
echo "$content" | grep -q "elements" || exit 1
```

### Output Handling

#### JSON output pattern (pure actions)
Pure actions output a single JSON object to avoid multiline delimiter issues:

```python
# Python pure action
output = {
    "version": version,
    "changelog": changelog_content,
    # or "release_notes": notes
}

json_str = json.dumps(output, ensure_ascii=False)

if gh_out := os.environ.get("GITHUB_OUTPUT"):
    with open(gh_out, "a", encoding="utf-8") as f:
        f.write(f"json_output={json_str}\n")
```

**Advantage:** single-line JSON avoids EOF delimiter parsing issues with special characters.

#### Parsing in workflows (using jq)
```yaml
- name: Extract from JSON output
  run: |
    json='${{ steps.my_pure_action.outputs.json_output }}'
    version=$(echo "$json" | jq -r '.version')
    changelog=$(echo "$json" | jq -r '.changelog')
```

### Versioning in uses

**Always specify version:**
```yaml
uses: ai-vibeqodez/dqwdwqd/.github/actions/release__resolve_next_release_pure@main
uses: ai-vibeqodez/dqwdwqd/.github/workflows/test__resolve_next_release_pure.yml@main
```

**Without version → error:**
```
Error: invalid value workflow reference: no version specified
```

Use:
- `@main` — for main branch
- `@v1.0.0` — for specific tag
- `@commit-sha` — for specific commit

---

## Parsing Strategies

### Conventional Commits Parsing

Format:
```
type(scope)?: description

optional body

optional footer
```

Regex (case-insensitive):
```regex
^(?P<type>[a-z]+)(?:\([^)]*\))?(?P<bang>!)?:\s*(?P<desc>.+)$
```

Examples:
- `feat: add auth` → type=feat, desc=add auth
- `feat(api)!: redesign` → type=feat, bang=!, desc=redesign
- `refactor!: remove old API` → breaking change

**Algorithm:**
```python
def parse_commits(commits_str: str) -> list[str]:
    # 1. Normalize \n (from GitHub Actions)
    commits_str = commits_str.replace("\\n", "\n")
    
    # 2. If multiline commits exist (separated by blank lines)
    if "\n\n" in commits_str:
        # Split by \n\n, each part is a commit with body
        commits_list = re.split(r'\n\n+', commits_str)
    else:
        # Otherwise each line is a separate single-line commit
        commits_list = commits_str.splitlines()
    
    return [c.strip() for c in commits_list if c.strip()]

def analyze_commits(commits: list[str]) -> dict:
    for commit_msg in commits:
        first_line = commit_msg.split("\n")[0]
        
        if m := re.match(PATTERN, first_line, re.I):
            is_breaking = m["bang"] or "BREAKING CHANGE" in commit_msg
            commit_type = m["type"]
            # → categorize into Breaking/Added/Fixed/etc
```

### Semantic Versioning Bumping

Base version: `(major, minor, patch)`

```python
if has_breaking_changes:
    next_version = f"{major + 1}.0.0"
elif has_features:
    next_version = f"{major}.{minor + 1}.0"
else:
    next_version = f"{major}.{minor}.{patch + 1}"
```

Priority: Breaking > Features > Fixes

### SemVer Parsing

```python
def parse_semver(raw: str) -> tuple[int, int, int] | None:
    if m := re.match(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$", raw.strip()):
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return None
```

Parses: "1.2.3" → (1, 2, 3), "0.0.1" → (0, 0, 1), "v1.2.3" → None (needs removeprefix)

### Changelog Parsing

Find first release as anchor:
```python
def find_changelog_version(changelog_text: str) -> tuple[int, int, int]:
    for line in changelog_text.splitlines():
        if m := re.match(r"^## \[([^\]]+)\]", line):
            if parsed := parse_semver(m.group(1)):
                return parsed
    return (0, 0, 0)
```

When inserting new release:
```python
if m_ver := re.search(r"^## \[(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)\]", content, re.M):
    # Insert before first existing release
    return content[:m_ver.start()] + new_release + "\n\n" + content[m_ver.start():]
else:
    # No releases → append at end
    return content.rstrip() + "\n\n" + new_release + "\n"
```

### Line Ending Preservation

```bash
# Detect CRLF
if file CHANGELOG.md | grep -q CRLF; then
    HAS_CRLF=true
else
    HAS_CRLF=false
fi
```

Python:
```python
def apply_line_ending(content: str, preserve_crlf: bool) -> str:
    if preserve_crlf:
        return content.replace("\n", "\r\n")
    return content
```

---

## Testing Pure Functions

### Strategy

Pure functions are fully deterministic and testable in isolation:
- **Input:** fixed strings (never change)
- **Output:** verify version, format, sections
- **Guarantee:** no flaky tests (doesn't depend on date, files, environment)

### Test Structure in GitHub Actions

```yaml
- id: test_case_name
  uses: ./.github/actions/release__resolve_next_release_pure@main
  with:
    raw_tags: 'v1.2.3'
    changelog_text: ''
    commits: 'feat: new feature'

- name: Verify test_case_name
  run: |
    json='${{ steps.test_case_name.outputs.json_output }}'
    version=$(echo "$json" | jq -r '.version')
    echo "Expected: 1.3.0, Got: $version"
    [[ "$version" == "1.3.0" ]] || exit 1
```

Use `if: always()` for summary steps to see all test results even if one fails:
```yaml
- name: Test Summary
  if: always()
  run: |
    echo "✓ All 20 test cases executed"
```

### Test Cases Examples (resolve_next_release_pure)

| Case | Input | Expected Output |
|------|-------|-----------------|
| No tags, no commits | `raw_tags=""` | `0.0.1` |
| v1.2.3, no commits | `raw_tags="v1.2.3"` | `1.2.4` (patch) |
| v1.2.3, feat commit | `commits="feat: add API"` | `1.3.0` (minor) |
| Breaking change | `commits="feat!: redesign"` | `2.0.0` (major) |
| Multiple feat + fix | `commits="feat:...\nfix:..."` | `1.3.0` (feat priority) |
| CHANGELOG v2.0.0, tag v1.0.0 | Mix | `2.0.1` (use max) |

### Test Cases Examples (write_release_files_pure)

| Case | Input | Verification |
|------|-------|------------|
| Empty CHANGELOG | `existing_changelog_content=""` | Has "# Changelog" header |
| Insert before existing | CHANGELOG has v0.5.0 | New v1.0.0 before v0.5.0 |
| Format check | `version="2.1.3", date="2024-06-15"` | Contains `## [2.1.3] - 2024-06-15` |
| Multiple releases | Add v2.0.0 to existing v1.0.0 | v2.0.0 first, v1.0.0 second |
| Special characters | notes with quotes, URLs | All preserved exactly |
| CRLF preservation | `preserve_crlf=true` | Line endings are `\r\n` |

---

## Debugging Tips

### Add logging to action

Python:
```python
import sys
print(f"DEBUG: version={version}, date={release_date}", file=sys.stderr)
print(f"DEBUG: changelog length={len(changelog_output)}", file=sys.stderr)
```

Bash:
```bash
echo "DEBUG: RAW_TAGS=$RAW_TAGS" >&2
echo "DEBUG: COMMITS count=$(echo "$COMMITS" | wc -l)" >&2
```

### Check GITHUB_OUTPUT before write

```python
if gh_out := os.environ.get("GITHUB_OUTPUT"):
    print(f"DEBUG: writing to {gh_out}", file=sys.stderr)
    with open(gh_out, "a", encoding="utf-8") as f:
        f.write(...)
else:
    print("ERROR: GITHUB_OUTPUT not set!", file=sys.stderr)
    sys.exit(1)
```

### If backticks cause problems

Use intermediate file:
```bash
cat > /tmp/verify.sh << 'EOF'
# Backticks here will be text, not interpreted
grep -q "Support for" "$content" || exit 1
EOF
bash /tmp/verify.sh
```

### Verify environment variables arrived

GitHub Actions logs all env vars:
```
env:
  INPUT_VERSION: 1.0.0
  INPUT_RELEASE_NOTES: ### Added\n- Feature
```

If empty — might be YAML escaping issue.

---

## Git & File Operations

### File Permissions in Git

If actions change file mode (executable bit), it's visible in git diff but not as content:
```
M	.github/workflows/release.yml
(0 insertions, 0 deletions)
```

VS Code may show file as "changed" due to permissions, while git status is clean.

**Solution:** use `git update-index --chmod`:
```bash
git update-index --chmod=-x .github/workflows/release.yml
git commit -m "fix: remove executable bit"
```

### Exclude files from git

If need to exclude workflow from versioning:
```bash
echo ".github/workflows/release.yml" >> .gitignore
git rm --cached .github/workflows/release.yml
git commit -m "Remove release.yml from tracking"
```

---

## Workflow Organization

### actions-test (workflow_dispatch)

Calls all test__*_pure workflows in parallel:
```yaml
on:
  workflow_dispatch:  # Run manually from UI

jobs:
  test__resolve_next_release_pure:
    uses: ./.github/workflows/test__resolve_next_release_pure.yml@main
  
  test__write_release_files_pure:
    uses: ./.github/workflows/test__write_release_files_pure.yml@main
```

Use for: verify all pure actions before release

### test__resolve_next_release_pure (workflow_call)

Called from actions-test, contains 21 test cases:
- 8 versioning tests (SemVer logic)
- 7 release notes sections tests
- 3 edge cases (breaking in body, scopes, multiple tags)
- 3 special cases tests

### reusable-release (workflow_call)

Can be called by other projects' workflows to publish release:
```yaml
jobs:
  - resolve_version: calls release__resolve_next_release_io
  - build: compiles artifacts
  - publish: calls release__write_release_files_io, creates git tag and GitHub release
```

---

## Anti-Patterns (what to avoid)

### ❌ Relative paths in uses
```yaml
# Bad
uses: ./.github/actions/my_action

# Good
uses: ai-vibeqodez/dqwdwqd/.github/actions/my_action@main
```

### ❌ IO and pure logic together
```python
# Bad: file and function in one
def compute_and_write(repo_dir):
    tags = subprocess.run(["git", "tag", ...])  # IO
    version = compute_version(tags)  # Pure
    with open("VERSION", "w") as f:  # IO
        f.write(version)

# Good: separate
def compute_version(tags_str):  # Pure, testable
    return ...

def io_layer(repo_dir):  # IO, orchestrates
    tags = subprocess.run(...)
    version = compute_version(tags)
    with open("VERSION", "w") as f:
        f.write(version)
```

### ❌ Hardcoded values in pure functions
```python
# Bad
def get_version():
    today = date.today()  # Depends on execution date
    return f"1.0.0-{today}"

# Good
def get_version(base_version, build_date):  # Parameters
    return f"{base_version}-{build_date}"
```

### ❌ No version in uses
```yaml
# Bad: will error
uses: ai-vibeqodez/dqwdwqd/.github/actions/my_action

# Good
uses: ai-vibeqodez/dqwdwqd/.github/actions/my_action@main
```

### ❌ Tests depend on execution order
```bash
# Bad: second test uses output from first
test_a_output=$(...)
test_b_uses_$test_a_output  # If test_a fails, test_b won't run

# Good: each test is independent
test_1_output=$(...)  # Independent, full setup
test_2_output=$(...)  # Independent, full setup
```

### ❌ Backticks without protection in bash
```bash
# Bad
grep -q "code" || exit 1  # If content has `code`, this fails

# Good
grep -q "elements" || exit 1  # Other parts of string
```

---

## Summary

| Component | When to use | Example |
|-----------|------------|---------|
| **_pure** | Calculations, parsing, data transformations | resolve_next_release_pure, write_release_files_pure |
| **_io** | Files, commands, environment, orchestration | resolve_next_release_io, write_release_files_io |
| **test__*_pure** | Test all scenarios of pure action | test__resolve_next_release_pure (21 test cases) |
| **actions-test** | Run all tests, verify before release | on: workflow_dispatch |

Result: **Maintainable, Testable, Deterministic, Debuggable Actions**
