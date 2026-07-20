#!/bin/sh
set -e

echo "[entrypoint] Esperando a PostgreSQL..."
until python -c "
import os, psycopg2
url = os.environ['DATABASE_URL'].replace('+psycopg2', '')
psycopg2.connect(url).close()
" 2>/dev/null; do
  sleep 1
done
echo "[entrypoint] PostgreSQL listo."

echo "[entrypoint] Aplicando migraciones..."
alembic upgrade head

echo "[entrypoint] Creando admin si no existe..."
python seed.py

echo "[entrypoint] Iniciando API..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
