#!/usr/bin/env bash
VENV_PY=./backend/.venv/bin/python
if [ -x "$VENV_PY" ]; then
  "$VENV_PY" -m pytest -q backend/tests
else
  python -m pytest -q backend/tests
fi
