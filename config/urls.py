"""
URLs principales du projet Django.
Inclut les URLs de l'application catalogue et gÃ¨re les mÃ©dias.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    # Favicon pour les navigateurs qui requièrent /favicon.ico à la racine
    path('favicon.ico', RedirectView.as_view(url='/static/catalogue/images/favicon.ico?v=2', permanent=False)),
    # Mot de passe oublié Admin
    path(
        "admin/password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="admin_password_reset",
    ),
    path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "admin/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "admin/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    # Interface d'administration Django
    path('rec/', admin.site.urls),
    # CKEditor upload endpoints
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # URLs de l'application catalogue (toutes les pages du site)
    path('', include('apps.catalogue.urls', namespace='catalogue')),
]

# En mode dÃ©veloppement, servir les fichiers mÃ©dia et statiques
if settings.DEBUG:
    # Fichiers mÃ©dia (images uploadÃ©es)
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    
    # Fichiers statiques (CSS, JS)
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
