# ── TOOD: FIXME ─────────────────────────────────────────────────────────────
# Everyday build targets.
#
#   make lint | build | test | clean
#
# Examples:
#   make lint
#   make build
#   make test

VERSION ?= 0.0.1

.PHONY: lint build test clean

lint:
	echo "OK"

build:
	mkdir -p dist
	echo "reusable workflows v${VERSION}" > dist/README.txt

test:
	echo "OK"

clean:
	rm -rf build
