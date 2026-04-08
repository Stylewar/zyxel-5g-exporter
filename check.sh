#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=${PYTHON:-"$ROOT_DIR/.venv/bin/python"}

if [ ! -x "$PYTHON" ]; then
    echo "Python interpreter not found: $PYTHON" >&2
    echo "Create the local environment first:" >&2
    echo "  python3 -m venv .venv" >&2
    echo "  .venv/bin/python -m pip install -r requirements.txt ruff" >&2
    exit 1
fi

"$PYTHON" -m py_compile "$ROOT_DIR/cellwan_exporter.py"
"$PYTHON" -m unittest discover -s "$ROOT_DIR/tests" -v
"$PYTHON" -m ruff check "$ROOT_DIR"
