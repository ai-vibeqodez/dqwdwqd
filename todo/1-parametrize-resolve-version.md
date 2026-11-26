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
- ✓ Workflow accepts `version_source` input
- ✓ Each source type correctly parses version
- ✓ Outputs `version` and `release_notes` consistently
- ✓ Backward compatible (no inputs = git_tags)
- ✓ All test cases pass

## Effort Estimate
2-3 hours

## Blocking Issues
None — pure logic
