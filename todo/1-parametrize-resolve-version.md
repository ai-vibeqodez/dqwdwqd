# 1-parametrize-resolve-version

## Goal
Параметризовать `reusable__release_resolve_version.yml` для поддержки разных источников версии: git tags, VERSION file, package.json, Cargo.toml.

## Context
Текущий workflow жестко привязан к одному action и работает только для проектов с git tags.

Нужна гибкость для:
- npm проектов (package.json)
- Rust проектов (Cargo.toml)
- C++ проектов (VERSION файл)
- Смешанных проектов (git tags как primary)

## Implementation Plan

### 1. Add input to `reusable__release_resolve_version.yml`
```yaml
on:
  workflow_call:
    inputs:
      version_source:
        type: choice
        required: false
        default: 'git_tags'
        options:
          - git_tags
          - version_file
          - package_json
          - cargo_toml
      version_file_path:
        type: string
        required: false
        default: 'VERSION'
```

### 2. Update resolve job
Branch logic based on `version_source`:
- `git_tags`: current behavior
- `version_file`: read and parse
- `package_json`: jq extraction
- `cargo_toml`: TOML parsing

### 3. Test cases
- npm project: resolve from package.json ✓
- Rust project: resolve from Cargo.toml ✓
- Generic project: resolve from VERSION file ✓
- Git tags priority ✓

## Acceptance Criteria
- ✓ Workflow accepts `version_source` input (git_tags, version_file, package_json, cargo_toml)
- ✓ Each source type correctly parses version
- ✓ Outputs `version` and `release_notes` consistently
- ✓ Backward compatible (no inputs = git_tags)
- ✓ All test cases pass

## Effort Estimate
2-3 hours

## Blocking Issues
None — pure logic

## Status
✓ COMPLETED

### Architecture:
- **Workflow** (`reusable__release_resolve_version.yml`): thin orchestrator, passes inputs through
- **IO Action** (`release__resolve_next_release_io`): collects data from different version sources
- **Pure Action** (`release__resolve_next_release_pure`): deterministic version bump logic (unchanged)

### What was done:
1. Added `version_source` and `version_file_path` inputs to `release__resolve_next_release_io` action
2. Implemented branching logic (case statement) in IO action's `collect` step:
   - `git_tags`: `git tag --merged HEAD --sort=-v:refname`
   - `version_file`: reads from VERSION or custom path
   - `package_json`: extracts version via jq
   - `cargo_toml`: parses with grep/sed
3. All sources normalize to `raw_tags` format (`vX.Y.Z`)
4. Workflow remains thin: just passes inputs to IO action
5. Created `test__parametrize_resolve_version.yml` testing IO action directly with 5 test cases
