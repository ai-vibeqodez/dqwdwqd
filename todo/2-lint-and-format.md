# 2-lint-and-format

## Goal
Создать `reusable__lint_and_format.yml` workflow для запуска linting и опционального auto-fix.

## Context
Часто нужно прогнать проект через linter перед commit/push. Workflow должен:
- Запустить `make lint` target
- Опционально: запустить `make fmt` и создать commit с исправлениями
- Работать для всех языков через Makefile
- Быть переиспользуемым в разных этапах CI

## Implementation Plan

### 1. Create `reusable__lint_and_format.yml`
```yaml
on:
  workflow_call:
    inputs:
      auto_fix:
        type: boolean
        required: false
        default: false
        description: 'Run make fmt and commit changes'
      commit_message:
        type: string
        required: false
        default: 'style: format code'
    outputs:
      passed:
        value: ${{ jobs.lint.outputs.passed }}
      files_changed:
        value: ${{ jobs.lint.outputs.files_changed }}
```

### 2. Job: lint
1. Checkout repo (with fetch-depth: 0 for history)
2. Run `make lint`
3. If lint fails: output summary and exit with error
4. If `auto_fix: true`:
   - Run `make fmt`
   - If files changed:
     - git config user
     - git add .
     - git commit -m "${{ inputs.commit_message }}"
     - git push origin HEAD
5. Output: passed (true/false), files_changed count

### 3. Test cases
- Lint passes → passed=true ✓
- Lint fails → passed=false, job fails ✓
- auto_fix=false → no commits ✓
- auto_fix=true + no changes → no commit ✓
- auto_fix=true + changes → creates and pushes commit ✓

## Acceptance Criteria
- ✓ Workflow runs linting via Makefile
- ✓ Fails job if linting fails
- ✓ Optional auto-fix commits changes
- ✓ Reports which files were changed
- ✓ Works with any language (through Makefile)

## Effort Estimate
1.5-2 hours

## Blocking Issues
None — requires Makefile `lint` and `fmt` targets (from ai-warevo-ci-setup)

## Usage Examples
```yaml
# Check only
uses: ./.github/workflows/reusable__lint_and_format.yml@main

# Auto-fix and commit
uses: ./.github/workflows/reusable__lint_and_format.yml@main
with:
  auto_fix: true
  commit_message: 'chore: auto-format code'
```

## Notes
- Assumes `make lint` and `make fmt` targets exist
- When auto_fix=true, requires write permissions (workflow permissions)
- If push fails (rebased branch), should handle gracefully
- Consider using `git push --force-with-lease` for safety
