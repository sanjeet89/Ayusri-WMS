#!/bin/bash
set -e

# Automatically map Railway's standard PostgreSQL environment variables (PGHOST, PGUSER, etc.) to InvenTree settings
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
