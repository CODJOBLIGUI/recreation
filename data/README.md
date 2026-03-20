# Sauvegarde des donnees (fixtures)

Ce dossier contient des exports JSON generes par Django.

## Exporter

Depuis le serveur :

```bash
python manage.py dumpdata --natural-foreign --natural-primary --indent 2 > data/backup.json
```

## Importer

Sur un autre environnement (base vide) :

```bash
python manage.py loaddata data/backup.json
```

Si la base contient deja des donnees, il est recommande de faire une sauvegarde avant l'import.
