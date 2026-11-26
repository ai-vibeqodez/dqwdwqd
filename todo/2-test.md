# 2-test

## Goal
Создать `reusable__test.yml` workflow для запуска тестов проекта с опциональной coverage.

## Context
Нужен переиспользуемый workflow для запуска тестов:
- Вызывает `make test` target (работает для любого языка)
- Опционально собирает coverage и публикует на Codecov
- Парсит результаты (JUnit XML, Go test output, etc)
- Работает в pre-release checks и в основном CI

## Implementation Plan

### 1. Create `reusable__test.yml`
```yaml
on:
  workflow_call:
    inputs:
      coverage:
        type: boolean
        required: false
        default: false
        description: 'Enable coverage reporting'
      codecov_token:
        type: string
        required: false
        description: 'Codecov token for uploading coverage'
    outputs:
      passed:
        value: ${{ jobs.test.outputs.passed }}
      coverage_percent:
        value: ${{ jobs.test.outputs.coverage_percent }}
      test_count:
        value: ${{ jobs.test.outputs.test_count }}
```

### 2. Job: test
1. Checkout repo
2. Run `make test`
3. If `coverage: true`:
   - Collect coverage data (make test should output coverage.xml or similar)
   - Parse coverage percentage
   - If `codecov_token` provided: upload to codecov.io
4. Parse test results (count passed/failed)
5. Generate summary report
6. Exit non-zero if tests fail

### 3. Test output parsing
- **Go**: parse `go test -v` output
- **npm**: parse Jest/Mocha JSON output
- **C++**: parse Google Test XML output
- **Generic**: count exit codes (simple pass/fail)

### 4. Coverage integration
- Expect coverage file at standard location: `coverage/coverage.xml` or `coverage.txt`
- Extract percentage and report as output
- Upload to codecov if token provided

### 5. Test cases
- All tests pass → passed=true ✓
- Some tests fail → passed=false, job fails ✓
- Coverage enabled, file generated → coverage_percent=85.5 ✓
- Coverage enabled, no file → warning but job passes ✓
- Codecov upload fails → warning, don't block job ✓

## Acceptance Criteria
- ✓ Workflow runs tests via Makefile
- ✓ Fails job if tests fail
- ✓ Optional coverage reporting
- ✓ Parses and outputs test count
- ✓ Codecov integration optional (doesn't block if unavailable)
- ✓ Works with any language (through Makefile)

## Effort Estimate
2-3 hours

## Blocking Issues
None — requires `make test` target from ai-warevo-ci-setup

## Usage Examples
```yaml
# Basic testing
uses: ./.github/workflows/reusable__test.yml@main

# With coverage (local only)
uses: ./.github/workflows/reusable__test.yml@main
with:
  coverage: true

# With Codecov upload
uses: ./.github/workflows/reusable__test.yml@main
with:
  coverage: true
  codecov_token: ${{ secrets.CODECOV_TOKEN }}
```

## Notes
- Makefile `test` target should handle coverage flag internally (or separate `coverage` target)
- Coverage file format varies by language; standardize via Makefile
- Codecov is optional; job should not fail if upload is unavailable
- Consider caching test artifacts if needed for debugging
