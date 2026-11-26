# 4-multiple-git-hosts

## Goal
Расширить workflows для поддержки различных Git-хостингов: GitHub, GitLab, Gitea, Forgejo.

## Context
Текущие workflows hardcoded для GitHub (gh CLI, github.token, etc).

Нужна поддержка для:
- **GitHub**: Current (gh CLI, github.token)
- **GitLab**: (glab CLI, CI_JOB_TOKEN)
- **Gitea**: (tea CLI, API tokens)
- **Forgejo**: (forgejo CLI, similar to Gitea)
- **Generic Git**: (plain git commands, no host-specific features)

## Implementation Plan

### 1. Add git_host input to reusable workflows
```yaml
on:
  workflow_call:
    inputs:
      git_host:
        type: choice
        required: false
        default: 'github'
        options:
          - github
          - gitlab
          - gitea
          - forgejo
          - generic
```

### 2. Parametrize host-specific logic
Branch on `git_host`:
- `github`: use `gh` CLI
- `gitlab`: use `glab` CLI or curl to GitLab API
- `gitea`: use `tea` CLI or curl to Gitea API
- `generic`: only git commands

### 3. Host-specific differences

| Feature | GitHub | GitLab | Gitea | Forgejo | Generic |
|---------|--------|--------|-------|---------|---------|
| **CLI tool** | `gh` | `glab` | `tea` | `forgejo` | `git` only |
| **Token env** | `GH_TOKEN` | `CI_JOB_TOKEN` | `GITEA_TOKEN` | `FORGEJO_TOKEN` | (none) |
| **Release creation** | `gh release create` | `glab release create` | API call | API call | ❌ Not supported |
| **Artifact upload** | `gh release upload` | `glab release upload` | API | API | ❌ Not supported |

### 4. Workflow changes
- `reusable__release_publish.yml`: add git_host input, determine command
- `reusable__release_resolve_version.yml`: add git_host input, fetch tags from API if needed

### 5. Environment setup per host
```bash
# GitHub
gh auth login --with-token <<< "$GH_TOKEN"

# GitLab
glab auth login --hostname gitlab.com --token "$CI_JOB_TOKEN"

# Gitea
export GITEA_TOKEN="$GITEA_TOKEN"
export GITEA_URL="https://git.example.com"
```

### 6. Test cases
- GitHub release creation ✓
- GitLab release creation ✓
- Gitea release creation ✓
- Forgejo release creation ✓
- Generic (git-only) path ✓
- Token passed correctly per host ✓
- Artifact upload per platform ✓

### 7. Documentation
- INTEGRATION.md: explain git_host input
- Sections for each platform setup
- Example tokens/credentials needed

## Acceptance Criteria
- ✓ Workflows accept `git_host` input
- ✓ Release creation works for each platform
- ✓ Token handling secure and platform-specific
- ✓ Generic path for unsupported platforms
- ✓ Artifact upload works (or skipped gracefully)
- ✓ Each platform tested end-to-end
- ✓ INTEGRATION.md updated

## Effort Estimate
4-6 hours

## Blocking Issues
- Access to GitLab/Gitea/Forgejo test instances needed

## Notes
- GitHub remains default (most common)
- For private Gitea/Forgejo: allow FQDN input
- Future: unified action for release creation
