VERSION ?= 0.0.1
PRESET  ?= msvc-debug

COVERAGE_PRESET ?= gcc-15-coverage

CLANG_FORMAT ?= clang-format-18
CLANG_TIDY   ?= clang-tidy-18

CPP_EXTS      := cpp cxx c hpp hxx h
CPP_FIND_ARGS := $(patsubst %,-o -name '*.%',$(CPP_EXTS))
CPP_EXT_REGEX := \.($(subst $(eval) ,|,$(CPP_EXTS)))$$

CPP_FILES        := $(shell find src include tests -type f \( -false $(CPP_FIND_ARGS) \) 2>/dev/null)
STAGED_CPP_FILES := $(shell git diff --cached --name-only --diff-filter=ACMR 2>/dev/null | grep -E '$(CPP_EXT_REGEX)' || true)

CMAKE_INSTALL_CONFIG := $(if $(findstring debug,$(PRESET)),Debug,Release)

.PHONY: help format format-staged lint lint-staged build test asan tsan coverage clean

help:
	@echo "Reusable Makefile (v$(VERSION), default PRESET=$(PRESET))"
	@echo ""
	@echo "Targets:"
	@echo "  make help           Show this help message"
	@echo "  make format         Format all C/C++ files with clang-format"
	@echo "  make format-staged  Format staged C/C++ files and re-add to git"
	@echo "  make lint           Run clang-format check and clang-tidy"
	@echo "  make lint-staged    Run lint checks on staged C/C++ files"
	@echo "  make build          Configure, build, and install (uses PRESET)"
	@echo "  make test           Run ctest suite (uses PRESET)"
	@echo "  make asan           Build and run tests with ASan + UBSan (gcc-15-asan)"
	@echo "  make tsan           Build and run tests with TSan (gcc-15-tsan)"
	@echo "  make coverage       Build, test, and generate coverage report ($(COVERAGE_PRESET))"
	@echo "  make clean          Remove build/ and dist/ directories"
	@echo ""
	@echo "Presets:"
	@echo "  gcc-15-debug | gcc-15-coverage | gcc-15-release | gcc-15-asan | gcc-15-tsan"
	@echo "  clang18-libcxx-debug | clang18-libcxx-release"
	@echo "  clang18-libstdcxx-debug | clang18-libstdcxx-release"
	@echo "  msvc-debug | msvc-release"
	@echo ""
	@echo "Examples:"
	@echo "  make build PRESET=gcc-15-debug"
	@echo "  make test  PRESET=gcc-15-debug"

format:
	@if [ -n "$(CPP_FILES)" ]; then \
		$(CLANG_FORMAT) -i $(CPP_FILES); \
	fi

format-staged:
	@if [ -n "$(STAGED_CPP_FILES)" ]; then \
		$(CLANG_FORMAT) -i $(STAGED_CPP_FILES); \
		git add $(STAGED_CPP_FILES); \
	else \
		echo "No staged C/C++ files to format"; \
	fi

lint:
	@if [ -n "$(CPP_FILES)" ]; then \
		$(CLANG_FORMAT) --dry-run --Werror $(CPP_FILES); \
		cmake --preset $(PRESET); \
		$(CLANG_TIDY) -p build/$(PRESET) --warnings-as-errors='*' $(CPP_FILES); \
	else \
		echo "OK"; \
	fi

lint-staged:
	@if [ -n "$(STAGED_CPP_FILES)" ]; then \
		$(CLANG_FORMAT) --dry-run --Werror $(STAGED_CPP_FILES); \
		cmake --preset $(PRESET); \
		$(CLANG_TIDY) -p build/$(PRESET) --warnings-as-errors='*' $(STAGED_CPP_FILES); \
	else \
		echo "No staged C/C++ files to lint"; \
	fi

build:
	cmake --preset $(PRESET)
	cmake --build --preset $(PRESET) --parallel
	cmake --install build/$(PRESET) --config $(CMAKE_INSTALL_CONFIG) --prefix dist/$(PRESET)

test:
	ctest --preset $(PRESET) --output-on-failure

asan:
	$(MAKE) build PRESET=gcc-15-asan
	$(MAKE) test PRESET=gcc-15-asan

tsan:
	$(MAKE) build PRESET=gcc-15-tsan
	@if command -v setarch >/dev/null 2>&1; then \
		setarch $$(uname -m) -R $(MAKE) test PRESET=gcc-15-tsan; \
	else \
		$(MAKE) test PRESET=gcc-15-tsan; \
	fi

coverage:
	$(MAKE) build PRESET=$(COVERAGE_PRESET)
	$(MAKE) test PRESET=$(COVERAGE_PRESET)
	@if command -v gcovr >/dev/null 2>&1; then \
		mkdir -p htmlcov; \
		GCOV_CMD=$$(grep '^COVERAGE_GCOV_EXECUTABLE' build/$(COVERAGE_PRESET)/CMakeCache.txt 2>/dev/null | cut -d= -f2); \
		if [ -z "$$GCOV_CMD" ]; then \
			GCOV_CMD="gcov"; \
		fi; \
		if ! command -v $$GCOV_CMD >/dev/null 2>&1; then \
			echo "ERROR: $$GCOV_CMD not found"; \
			exit 1; \
		fi; \
		PWD_ABS=$$(pwd); \
		FILTER_ARGS="--filter $$PWD_ABS/src/ --filter $$PWD_ABS/include/"; \
		if [ -n "$(GCOVR_FILTER)" ]; then \
			FILTER_ARGS="$$FILTER_ARGS --filter $$PWD_ABS/$(GCOVR_FILTER)"; \
		fi; \
		EXCLUDE_ARGS=""; \
		if [ -n "$(GCOVR_EXCLUDE)" ]; then \
			EXCLUDE_ARGS="--exclude $(GCOVR_EXCLUDE)"; \
		fi; \
		gcovr -r . build/$(COVERAGE_PRESET) --gcov-executable $$GCOV_CMD $$FILTER_ARGS $$EXCLUDE_ARGS --gcov-ignore-errors=no_working_dir_found --exclude-unreachable-branches --exclude-throw-branches --print-summary --xml coverage.xml --html-details htmlcov/index.html; \
		echo "✓ Coverage report: htmlcov/index.html"; \
	else \
		echo "ERROR: gcovr not found"; \
		exit 1; \
	fi

clean:
	rm -rf build dist
