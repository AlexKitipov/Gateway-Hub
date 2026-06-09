#!/bin/sh
# Run database migrations explicitly before starting or restarting the API.
set -eu

echo "Running database migrations with Alembic..."
alembic upgrade head
