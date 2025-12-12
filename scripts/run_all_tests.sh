#!/usr/bin/env bash
set -euo pipefail

# Run all tests: backend unit, integration, frontend e2e (Unix-like)
ROOT=$(cd $(dirname "$0")/.. && pwd)
cd "$ROOT"
export PYTHONPATH="$ROOT"

# Env flags:
# SKIP_E2E=1 -> skip frontend e2e
# FORCE_E2E=1 -> fail if e2e cannot run (npm missing)
SKIP_E2E=${SKIP_E2E:-0}
FORCE_E2E=${FORCE_E2E:-0}
export PYTHONPATH="$ROOT"

# Clean DB
[ -f "./ecommerce.db" ] && rm -f ./ecommerce.db
[ -f "./backend/ecommerce.db" ] && rm -f ./backend/ecommerce.db
[ -f "./ecommerce_test.db" ] && rm -f ./ecommerce_test.db

# Backend deps
pushd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
popd

# Backend tests (unit + integration together while server is running)

# Integration tests: start uvicorn with test DB
echo "Running backend tests (unit + integration) with coverage..."
export DATABASE_URL="sqlite:///./ecommerce_test.db"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
UVICORN_PID=$!
sleep 2
set +e
# Run full backend test suite and generate coverage
python -m pytest --cov=backend --cov-report=xml:coverage.xml backend/tests -q -vv
TEST_RC=$?
set -e
kill $UVICORN_PID || true
sleep 1
rm -f ./ecommerce_test.db || true

# Frontend e2e
echo "Running frontend e2e tests..."
if [ "${SKIP_E2E}" = "1" ]; then
	echo "SKIP_E2E=1 set; skipping frontend e2e tests."
else
	if ! command -v npm >/dev/null 2>&1; then
		if [ "${FORCE_E2E}" = "1" ]; then
			echo "npm not found in PATH and FORCE_E2E=1; failing." >&2
			exit 2
		fi
		echo "npm not found in PATH; skipping frontend e2e tests."
	else
		pushd frontend
		npm ci
		npx playwright install --with-deps
		# Start backend and frontend
		python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
		BACKEND_PID=$!
		npm run dev &
		FRONTEND_PID=$!
		sleep 4
		set +e
		npm run test:e2e
		E2E_RC=$?
		set -e
		# Teardown
		kill $FRONTEND_PID || true
		kill $BACKEND_PID || true
		popd
	fi
fi

# Propagate failures
if [ "${TEST_RC:-0}" != "0" ]; then
	echo "Integration tests failed (rc=${TEST_RC})." >&2
	exit ${TEST_RC}
fi
if [ "${E2E_RC:-0}" != "0" ]; then
	echo "E2E tests failed (rc=${E2E_RC})." >&2
	exit ${E2E_RC}
fi

echo "All tests completed."
