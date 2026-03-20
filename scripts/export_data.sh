#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p data

python manage.py dumpdata --natural-foreign --natural-primary --indent 2 > data/backup.json

echo "Backup created at: $ROOT_DIR/data/backup.json"
echo "Next:"
echo "  git add data/backup.json"
echo "  git commit -m \"Backup data from admin\""
echo "  git push origin master"
