#!/usr/bin/env bash
set -euo pipefail

# === Mise à jour sur PythonAnywhere ===
cd ~/recreation

# Activer le venv
source ~/.virtualenvs/recreation-venv/bin/activate

# Pull + migrations + statiques
git pull origin master
python manage.py migrate
python manage.py collectstatic --noinput

# Recharger l'app (reload.txt)
touch reload.txt
