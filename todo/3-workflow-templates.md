# 3-workflow-templates

## Goal
Создать templates directory в central repo с `.github/workflows/release.yml.template` files для быстрого старта новых проектов.

## Context
Новые проекты могут копировать готовые шаблоны вместо ручного написания `release.yml` с нуля.

Шаблоны для:
- Базовый проект (`release.yml.template`)
- Node.js/npm (`release.npm.yml.template`)
- C++/CMake (`release.cpp.yml.template`)
- Go (`release.go.yml.template`)
- Python (`release.python.yml.template`)
- Rust (`release.rust.yml.template`)
- Docker (`release.docker.yml.template`)

Каждый шаблон должен быть:
- Полностью рабочим (copy-paste ready)
- С комментариями для настройки
- С inline примерами значений
- Минимальным но полным

## Implementation Plan

### 1. Create templates directory structure
```
templates/
├── README.md                           # How to use templates
├── release.yml.template                # Generic template
├── release.npm.yml.template            # Node.js specific
├── release.cpp.yml.template            # C++ specific
├── release.go.yml.template             # Go specific
├── release.python.yml.template         # Python specific
├── release.rust.yml.template           # Rust specific
└── release.docker.yml.template         # Docker-specific
```

### 2. Generic template: `release.yml.template`

```yaml
name: release

on:
  workflow_dispatch:

permissions:
  contents: write
  actions: write

jobs:
  resolve_version:
    uses: ai-vibeqodez/dqwdwqd/.github/workflows/reusable__release_resolve_version.yml@main

  checks:
    uses: ai-vibeqodez/dqwdwqd/.github/workflows/reusable__pre_release_checks.yml@main

  build:
    needs: [resolve_version, checks]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    needs: [resolve_version, build]
    uses: ai-vibeqodez/dqwdwqd/.github/workflows/reusable__release_publish.yml@main
    with:
      version: ${{ needs.resolve_version.outputs.version }}
      release_notes: ${{ needs.resolve_version.outputs.release_notes }}
```

### 3. npm template: `release.npm.yml.template`

```yaml
name: release

on:
  workflow_dispatch:

permissions:
  contents: write
  actions: write
  packages: write

jobs:
  resolve_version:
    uses: ai-vibeqodez/dqwdwqd/.github/workflows/reusable__release_resolve_version.yml@main
    with:
      version_source: 'package_json'

  checks:
    uses: ai-vibeqodez/dqwdwqd/.github/workflows/reusable__pre_release_checks.yml@main

  build:
    needs: [resolve_version, checks]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci && make build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    needs: [resolve_version, build]
    uses: ai-vibeqodez/dqwdwqd/.github/workflows/reusable__release_publish.yml@main
    with:
      version: ${{ needs.resolve_version.outputs.version }}
      release_notes: ${{ needs.resolve_version.outputs.release_notes }}
```

## Acceptance Criteria
- ✓ All 7 templates created in `templates/`
- ✓ Each template is complete and copy-paste ready
- ✓ Inline comments explain customization points
- ✓ All templates tested (at least locally)
- ✓ README.md explains how to use templates
- ✓ No broken references to workflows

## Effort Estimate
2-3 hours

## Blocking Issues
None — templates are standalone reference files

## Notes
- Templates use comments to highlight what to customize
- Keep templates close to documented examples in INTEGRATION.md
- Update templates when workflows change significantly
- Consider versioning templates later
