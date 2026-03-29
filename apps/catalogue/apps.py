"""
Configuration de l'application catalogue.
"""

from django.apps import AppConfig


class CatalogueConfig(AppConfig):
    """Configuration de l'application catalogue."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.catalogue'
    verbose_name = 'Catalogue de livres'

