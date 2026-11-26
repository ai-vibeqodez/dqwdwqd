# 1-pre-release-checks

## Goal
Создать `reusable__pre_release_checks.yml` для валидации проекта перед release (lint, test, security).

## Context
Текущий `release.yml` идет прямо от resolve → build → publish без проверок.

Нужен workflow который:
- Запускает project Makefile targets (`lint`, `test`, `security-scan`)
- Собирает результаты в summary
- Блокирует publish если что-то не прошло
- Работает для всех языков через Makefile

## Implementation Plan

### 1. Create `reusable__pre_release_checks.yml`
```yaml
on:
  workflow_call:
    inputs:
      check_targets:
        type: string
        required: false
        default: 'lint test'
        description: 'Makefile targets (space-separated)'
    outputs:
      all_passed:
        value: ${{ jobs.checks.outputs.all_passed }}
      summary:
        value: ${{ jobs.checks.outputs.summary }}
```

### 2. Job: pre_release_checks
1. Checkout repo
2. For each target: run `make $target`, capture exit code
3. Output summary: "lint ✓, test ✓, security ✗"
4. Exit non-zero if any failed

### 3. Update `release.yml` to use it
```yaml
jobs:
  checks:
    uses: ./.github/workflows/reusable__pre_release_checks.yml@main
    with:
      check_targets: 'lint test'
  
  build:
    needs: [resolve_version, checks]
```

### 4. Test cases
- Makefile has lint, test → runs both ✓
- Makefile missing test → skips gracefully ✓
- Lint fails → blocks build ✓
- Security target available → runs ✓
- Empty check_targets → no-op ✓

## Acceptance Criteria
- ✓ Accepts `check_targets` input
- ✓ Runs targets if available
- ✓ Collects results and outputs summary
- ✓ Fails job if any check fails
- ✓ Works with projects missing some targets
- ✓ Can be used before build or publish

## Effort Estimate
1-2 hours

## Blocking Issues
None — requires Makefile in project

## Notes
- Assumes Makefile at repo root (follow ai-warevo-ci-setup)
- Fail with helpful error if Makefile missing
- Optional: support custom check scripts as fallback
