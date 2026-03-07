#!/bin/bash
echo "🔄 Exécution des migrations..."
python manage.py migrate --noinput
echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput
echo "🚀 Démarrage de Gunicorn..."
gunicorn config.wsgi:application --log-file -
