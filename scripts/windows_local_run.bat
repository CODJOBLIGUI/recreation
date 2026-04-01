@echo off
setlocal

REM === Lancer le site en local (Windows) ===
cd /d C:\Users\User\Desktop\recreation-master\recreation-master

REM Migrations
.\venv\Scripts\python.exe manage.py migrate

REM Démarrer le serveur
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000

endlocal
