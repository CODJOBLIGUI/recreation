# Procédures Recréation (Résumé)

## Annuler une modification locale
```bash
git restore <fichier>
```

## Recharger le cache des templates (PythonAnywhere)
```bash
cd ~/recreation
git pull
source ~/.virtualenvs/recreation-venv/bin/activate
python manage.py collectstatic --noinput
touch reload.txt
```

## Supprimer les audios et fichiers de conversion
```bash
rm -rf ~/recreation/media/audio_requests/audio/*
rm -rf ~/recreation/media/audio_requests/files/*
```

## Migrations simples (PythonAnywhere)
```bash
cd ~/recreation
source ~/.virtualenvs/recreation-venv/bin/activate
git pull
python manage.py migrate
```

## Procédure complète (backup + pull + migrate + statiques)
```bash
cd ~/recreation

# Sauvegarde DB
mkdir -p backups
cp db.sqlite3 backups/db.sqlite3.pa_$(date +%Y%m%d_%H%M%S)

# Pull propre
git fetch origin
git restore config/settings/base.py
git stash push -m "keep-db" db.sqlite3
git pull origin master
git checkout stash@{0} -- db.sqlite3
git stash drop

# Migrations + statiques
source ~/.virtualenvs/recreation-venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

## En cas de conflit de migrations (PythonAnywhere)
```bash
cd ~/recreation
source ~/.virtualenvs/recreation-venv/bin/activate

python manage.py makemigrations --merge core
python manage.py migrate
python manage.py collectstatic --noinput
```

## Lancer le site en local (Windows)
```powershell
cd C:\Users\User\Desktop\recreation-master\recreation-master
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Ouvrir :
```
http://127.0.0.1:8000/
```

## Push (Windows PowerShell)
```powershell
cd C:\Users\User\Desktop\recreation-master\recreation-master
git add <fichiers>
git commit -m "message"
git push origin master
```

## Actualiser le site en ligne (PythonAnywhere)
```bash
cd ~/recreation
git pull
source ~/.virtualenvs/recreation-venv/bin/activate
python manage.py collectstatic --noinput
```
