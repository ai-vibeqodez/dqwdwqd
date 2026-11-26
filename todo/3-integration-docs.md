# 3-integration-docs

## Goal
Создать `INTEGRATION.md` с полной документацией для интеграции central CI инфраструктуры.

## Context
Нужна четкая, пошаговая инструкция:
- Как подключить reusable workflows в проект
- Какие workflows доступны
- Copy-paste templates для разных языков
- Как настроить Makefile
- Troubleshooting и FAQ

## Implementation Plan

### 1. Document Structure
```
INTEGRATION.md
├── Overview
├── Quick Start (5 min)
├── Available Workflows (reference table)
├── Templates by Language
│   ├── Node.js / npm
│   ├── C++ / CMake
│   ├── Go
│   ├── Python
│   └── Rust
├── Makefile Contract
├── GitHub Setup
├── Troubleshooting
├── FAQ
└── Examples
```

### 2. Key sections
- Overview: 1-paragraph summary + benefits
- Quick Start: 5 concrete steps, 5 minutes
- Workflows Reference: table with inputs/outputs
- Language Templates: copy-paste ready examples
- Makefile Contract: required targets per language
- Troubleshooting: organized by error message
- FAQ: common questions

### 3. Test cases for docs
- npm template works end-to-end ✓
- C++ template works with matrix ✓
- Go template works ✓
- Troubleshooting resolves common issues ✓

## Acceptance Criteria
- ✓ INTEGRATION.md complete and published
- ✓ All 5 language templates present and tested
- ✓ Quick Start works in <5 minutes
- ✓ Makefile contract documented
- ✓ Troubleshooting covers common errors
- ✓ Examples are copy-paste ready

## Effort Estimate
4-6 hours

## Blocking Issues
Depends on workflows from Priority 1-2 being mostly stable

## Notes
- Keep examples minimal but complete
- Test each template in actual project
- Link to central repo workflows
