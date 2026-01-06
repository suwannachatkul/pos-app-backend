#!/bin/bash
set -e

echo "Running database migrations..."
python -m alembic upgrade head

echo "Starting API server..."
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
