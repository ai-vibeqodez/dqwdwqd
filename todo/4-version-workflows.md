# 4-version-workflows

## Goal
Перейти с `@main` на семантическое версионирование для reusable workflows (`@v1.0.0`, `@v2.0.0`).

## Context
Текущие workflows используют `@main`, что означает:
- Любое изменение немедленно влияет на все проекты
- Нет стабильности, нет обратной совместимости
- Сложно отследить, какая версия использовалась

Нужно:
- Создать первый stable release `v1.0.0`
- Версионировать саму инфраструктуру через CHANGELOG.md
- Позволить проектам lock версию и обновляться consciously
- Документировать breaking changes

## Implementation Plan

### 1. Versioning strategy
- **Major**: Breaking changes
- **Minor**: New optional inputs, non-breaking enhancements
- **Patch**: Bug fixes, internal improvements

### 2. Create CHANGELOG.md for workflows
Document v1.0.0 release with all added workflows and features

### 3. Tagging and release process
1. Update CHANGELOG.md with new version
2. Commit: `git commit -m "docs: release v1.0.0"`
3. Tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push: `git push origin main --tags`
5. Create GitHub Release from tag

### 4. Update docs to reference v1.0.0
- INTEGRATION.md
- templates/*.yml.template
- README.md

### 5. Migration path
- Phase 1: New projects use @v1.0.0
- Phase 2: Notices to @main users
- Phase 3: Deprecate @main (after 6+ months)

### 6. Test cases
- New project using @v1.0.0 → resolves correctly ✓
- Project using @main → still works ✓
- Migrate from @main to @v1.0.0 → no changes needed ✓
- Future breaking change → v2.0.0 documented ✓

## Acceptance Criteria
- ✓ CHANGELOG.md created and maintained
- ✓ First release tagged as v1.0.0
- ✓ INTEGRATION.md references v1.0.0
- ✓ Templates reference v1.0.0
- ✓ GitHub Release created with notes
- ✓ Clear versioning policy documented

## Effort Estimate
1-2 hours

## Blocking Issues
Depends on workflows being stable and tested

## Notes
- v1.0.0 doesn't mean perfect, just stable and documented
- After v1.0.0, reserve breaking changes for major versions
- Document all breaking changes clearly in CHANGELOG
