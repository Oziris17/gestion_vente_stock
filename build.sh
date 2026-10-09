#!/usr/bin/env bash
# arrêter le script à la première erreur
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py creer_roles
python manage.py createsuperuser --noinput || true