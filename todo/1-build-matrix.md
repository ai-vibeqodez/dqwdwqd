# 1-build-matrix

## Goal
Создать `reusable__build_matrix.yml` workflow для поддержки matrix builds (компиляторы, платформы, версии).

## Context
Текущий build job не поддерживает matrix. Нужна переиспользуемая workflow для:
- C++ проектов: matrix по gcc/clang версиям
- Go проектов: matrix по версиям и платформам
- Rust проектов: matrix по toolchain версиям

## Implementation Plan

### 1. Create `reusable__build_matrix.yml`
```yaml
on:
  workflow_call:
    inputs:
      matrix_strategy:
        type: choice
        default: 'generic'
        options:
          - generic
          - cpp
          - go
          - rust
          - cross-platform
      matrix_config:
        type: string
        required: false
        default: '{}'
    outputs:
      artifacts_uploaded:
        value: ${{ jobs.build.outputs.artifacts_uploaded }}
```

### 2. Job: build_matrix
- Determine matrix based on strategy
- For each combo: setup environment, `make build`, upload artifact
- Artifact naming: `dist-gcc11-linux`, etc

### 3. Matrix definitions
- **cpp**: compiler + version combinations
- **go**: go-version + os combinations
- **rust**: rust-version + os combinations

### 4. Test case: template_cpp
- Use matrix_strategy: cpp
- Build with gcc 11, 12, 13 and clang 14, 15
- Verify all 10 artifacts uploaded

## Acceptance Criteria
- ✓ Accepts `matrix_strategy` input
- ✓ Generates correct matrix per strategy
- ✓ Builds all combinations
- ✓ Artifacts labeled with matrix params
- ✓ Works with existing Makefile
- ✓ template_cpp demonstrates usage
- ✓ Backward compatible with generic

## Effort Estimate
3-4 hours

## Blocking Issues
Depends on template_cpp existing

## Notes
- Each matrix combo = separate artifact
- Matrix identifier in artifact name
- Consider timeout per job for slow builds
