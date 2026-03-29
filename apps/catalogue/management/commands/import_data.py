# apps/catalogue/management/commands/import_data.py

import os
from datetime import date
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from apps.catalogue.models import Auteur, Collection, Livre

class Command(BaseCommand):
    help = 'Importe les données initiales des auteurs et des livres dans la base de données.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Début de l\'importation des données ---'))
        
        # Nettoyer les anciennes données pour éviter les doublons
        self.stdout.write('Nettoyage des anciennes données...')
        Livre.objects.all().delete()
        Auteur.objects.all().delete()
        Collection.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Anciennes données supprimées.'))

        # --- Données des Auteurs ---
        auteurs_data = [
            {'id': 1, 'nom': 'Amine Abbanou Badjoury', 'specialite': 'Romancier', 'photo': 'amine_abbanou_badjoury.png', 'biographie': 'Biographie de Amine Abbanou Badjoury...'},
            {'id': 2, 'nom': 'Gratien G. Makoko', 'specialite': 'Essayiste', 'photo': 'gratien_makoko.avif', 'biographie': 'Biographie de Gratien G. Makoko...'},
            {'id': 3, 'nom': 'Emilie Magnima', 'specialite': 'Poétesse', 'photo': 'emilie_magnima.png', 'biographie': 'Biographie de Emilie Magnima...'},
            {'id': 4, 'nom': 'Marel Fleuri', 'specialite': 'Romancier', 'photo': 'marel_fleuri.avif', 'biographie': 'Biographie de Marel Fleuri...'},
        ]

        auteurs_map = {}
        self.stdout.write('Importation des auteurs...')
        for data in auteurs_data:
            auteur = Auteur.objects.create(
                nom=data['nom'],
                specialite=data['specialite'],
                biographie=data['biographie']
            )
            # Gestion de l\'image
            photo_path = os.path.join(settings.BASE_DIR, 'apps', 'catalogue', 'static', 'catalogue', 'images', 'authors', data['photo'])
            if os.path.exists(photo_path):
                with open(photo_path, 'rb') as f:
                    auteur.photo.save(data['photo'], File(f), save=True)
            
            auteurs_map[data['id']] = auteur
            self.stdout.write(f'  - Auteur créé : {auteur.nom}')
        self.stdout.write(self.style.SUCCESS(f'{len(auteurs_data)} auteurs importés.'))

        # --- Données des Collections ---
        collections_data = [
            {"nom": "Voix d'Ailleurs"},
            {"nom": "Plumes du Continent"},
            {"nom": "Échos Poétiques"},
            {"nom": "Noir Désir"},
        ]

        collections_map = {}
        self.stdout.write('Importation des collections...')
        for data in collections_data:
            collection = Collection.objects.create(nom=data["nom"])
            collections_map[data["nom"]] = collection
            self.stdout.write(f'  - Collection créée : {collection.nom}')
        self.stdout.write(self.style.SUCCESS(f'{len(collections_data)} collections importées.'))

        # --- Données des Livres ---
        livres_data = [
            {'titre': 'Julia', 'auteur_id': 1, 'categorie': 'roman', 'collection': 'Voix d\'Ailleurs', 'parution': date(2023, 5, 20), 'prix': '10000 FCFA', 'isbn': '978-999-1', 'image': 'julia.jpg', 'est_bestseller': True, 'resume': 'Résumé du livre Julia...'},
            {'titre': 'Les prémices d\'une vie', 'auteur_id': 2, 'categorie': 'essai', 'collection': 'Plumes du Continent', 'parution': date(2022, 11, 10), 'prix': '8500 FCFA', 'isbn': '978-999-2', 'image': 'les_premices.jpg', 'est_nouveau': True, 'resume': 'Résumé de Les prémices d\'une vie...'},
            {'titre': 'Murmures de l\'âme', 'auteur_id': 3, 'categorie': 'poemes', 'collection': 'Échos Poétiques', 'parution': date(2024, 1, 15), 'prix': '7000 FCFA', 'isbn': '978-999-3', 'image': 'murmures.jpeg', 'est_nouveau': True, 'resume': 'Résumé de Murmures de l\'âme...'},
            {'titre': 'La Criet, une réclusion criminelle', 'auteur_id': 4, 'categorie': 'policiers', 'collection': 'Noir Désir', 'parution': date(2023, 8, 30), 'prix': '12000 FCFA', 'isbn': '978-999-4', 'image': 'la_criet.jpeg', 'resume': 'Résumé de La Criet...'},
        ]

        self.stdout.write('Importation des livres...')
        for data in livres_data:
            auteur = auteurs_map.get(data['auteur_id'])
            if not auteur:
                self.stdout.write(self.style.WARNING(f'Auteur ID {data["auteur_id"]} non trouvé pour le livre "{data["titre"]}". Livre non importé.'))
                continue

            livre = Livre.objects.create(
                titre=data['titre'],
                categorie=data['categorie'],
                collection=collections_map.get(data.get('collection', '')),
                resume=data['resume'],
                isbn=data['isbn'],
                prix=data['prix'],
                parution=data['parution'],
                est_nouveau=data.get('est_nouveau', False),
                est_bestseller=data.get('est_bestseller', False)
            )
            livre.auteurs.add(auteur)
            # Gestion de l\'image
            image_path = os.path.join(settings.BASE_DIR, 'apps', 'catalogue', 'static', 'catalogue', 'images', 'books', data['image'])
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    livre.image.save(data['image'], File(f), save=True)

            self.stdout.write(f'  - Livre créé : {livre.titre}')
        self.stdout.write(self.style.SUCCESS(f'{len(livres_data)} livres importés.'))

        self.stdout.write(self.style.SUCCESS('--- Importation terminée avec succès ! ---'))

