"""
URLs principales du projet Django.
Inclut les URLs de l'application catalogue et gère les médias.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    # Favicon pour les navigateurs qui requièrent /favicon.ico à la racine
    path('favicon.ico', RedirectView.as_view(url='/static/catalogue/images/favicon.ico?v=2', permanent=False)),
    # Interface d'administration Django
    path('edrecreation/', admin.site.urls),
    # CKEditor 5 endpoints
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    
    # URLs de l'application catalogue (toutes les pages du site)
    path('', include('apps.catalogue.urls', namespace='catalogue')),
]

# En mode développement, servir les fichiers média et statiques
if settings.DEBUG:
    # Fichiers média (images uploadées)
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    
    # Fichiers statiques (CSS, JS)
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
