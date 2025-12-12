#!/bin/sh
set -e
# Wait for DB (if needed), run migrations, then start the server
python wait_for_db.py
python migrate.py
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
