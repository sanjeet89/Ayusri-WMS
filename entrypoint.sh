#!/bin/bash
set -e

# Map Railway PORT to InvenTree web port
if [ -n "$PORT" ]; then
    export INVENTREE_WEB_PORT="$PORT"
else
    export INVENTREE_WEB_PORT="${INVENTREE_WEB_PORT:-8000}"
fi

# Allow Railway domains / proxy headers
export INVENTREE_ALLOWED_HOSTS="${INVENTREE_ALLOWED_HOSTS:-*}"
export INVENTREE_USE_X_FORWARDED_HOST="True"
export INVENTREE_USE_X_FORWARDED_PORT="True"
export INVENTREE_USE_X_FORWARDED_PROTO="True"

# Automatically map Railway's standard PostgreSQL environment variables (PGHOST, PGUSER, etc.)
export INVENTREE_DB_ENGINE="${INVENTREE_DB_ENGINE:-postgresql}"
export INVENTREE_DB_HOST="${INVENTREE_DB_HOST:-${PGHOST:-inventree-db}}"
export INVENTREE_DB_PORT="${INVENTREE_DB_PORT:-${PGPORT:-5432}}"
export INVENTREE_DB_NAME="${INVENTREE_DB_NAME:-${PGDATABASE:-${POSTGRES_DB:-inventree}}}"
export INVENTREE_DB_USER="${INVENTREE_DB_USER:-${PGUSER:-pguser}}"
export INVENTREE_DB_PASSWORD="${INVENTREE_DB_PASSWORD:-${PGPASSWORD:-pgpassword}}"

# Forward execution to InvenTree's base entrypoint if available
if [ -x /home/inventree/docker/entrypoint.sh ]; then
    exec /home/inventree/docker/entrypoint.sh "$@"
else
    exec "$@"
fi
