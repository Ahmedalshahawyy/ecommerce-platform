#!/usr/bin/env bash
# Run Alembic upgrade head using venv python if available
VENV_PY=./backend/.venv/bin/python
if [ -x "$VENV_PY" ]; then
  "$VENV_PY" ./backend/migrate.py
else
  python ./backend/migrate.py
fi
