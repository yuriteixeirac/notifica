#!/bin/sh
set -e

echo "⏳ Aguardando MariaDB..."
until nc -z "$DB_HOST" "${DB_PORT:-3306}"; do
  sleep 1
done
echo "✅ MariaDB disponível."

echo "⏳ Aguardando Redis..."
until nc -z "$REDIS_HOST" "${REDIS_PORT:-6379}"; do
  sleep 1
done
echo "✅ Redis disponível."

echo "🔄 Aplicando migrações..."
python manage.py migrate --noinput

echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "🚀 Iniciando aplicação..."
exec "$@"
