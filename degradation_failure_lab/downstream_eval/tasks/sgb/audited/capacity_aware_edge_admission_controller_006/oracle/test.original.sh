#!/bin/bash
set -e

mkdir -p /logs/verifier
export TEST_ROOT_DIR=/workspace
PYTHON_BIN="${PYTHON:-python3}"

if ! "$PYTHON_BIN" -m pytest --version >/dev/null 2>&1; then
    "$PYTHON_BIN" -m pip install --break-system-packages pytest==8.4.1 pytest-json-ctrf==0.3.5 >/dev/null 2>&1 || true
fi

if [ -f /workspace/tests/eval.py ]; then
    TEST_TARGET=/workspace/tests/eval.py
else
    TEST_TARGET=/workspace/tests/test_*.py
fi

set +e
if "$PYTHON_BIN" -m pytest --help 2>/dev/null | grep -q -- "--ctrf"; then
    "$PYTHON_BIN" -m pytest --ctrf /logs/verifier/ctrf.json $TEST_TARGET -rA -v
    PYTEST_EXIT=$?
else
    "$PYTHON_BIN" -m pytest $TEST_TARGET -rA -v
    PYTEST_EXIT=$?
fi
set -e

if [ ! -f /logs/verifier/ctrf.json ]; then
    if [ $PYTEST_EXIT -eq 0 ]; then
        cat > /logs/verifier/ctrf.json <<'JSON'
{"results": {"summary": {"tests": 1, "passed": 1, "failed": 0}}}
JSON
    else
        cat > /logs/verifier/ctrf.json <<'JSON'
{"results": {"summary": {"tests": 1, "passed": 0, "failed": 1}}}
JSON
    fi
fi

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
