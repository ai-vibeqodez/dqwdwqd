# ── Reusable Makefile ──────────────────────────────────────────────────────
# Everyday build targets.
#
#   make lint | build | test | clean
#
# Examples:
#   make lint
#   make build
#   make test
#   make build PRESET=gcc-15-debug
#   make build PRESET=gcc-15-release
#   make build PRESET=gcc-15-asan
#   make build PRESET=gcc-15-tsan
#   make build PRESET=msvc-debug
#   make build PRESET=msvc-release
#   make build PRESET=clang18-libcxx-debug
#   make build PRESET=clang18-libcxx-release
#   make build PRESET=clang18-libstdcxx-debug
#   make build PRESET=clang18-libstdcxx-release

VERSION ?= 0.0.1
PRESET  ?= msvc-release

.PHONY: lint build test clean

lint:
	echo "OK"

build:
	mkdir -p dist
	echo "cmake --preset ${PRESET}"
	echo "reusable workflows v${VERSION} (${PRESET})" > dist/README_${PRESET}.txt

test:
	echo "OK"

clean:
	rm -rf build dist
