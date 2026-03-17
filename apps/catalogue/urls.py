"""
FICHIER : apps/catalogue/urls.py
"""

from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .forms import StyledLoginForm
from . import views

app_name = 'catalogue'

urlpatterns = [
    # Pages principales
    path('', views.IndexView.as_view(), name='index'),
    path('catalogue/', views.CatalogueView.as_view(), name='catalogue'),
    path('livres-numeriques/', views.LivresNumeriquesView.as_view(), name='livres-numeriques'),
    path('livres-papier/', views.LivresPapierView.as_view(), name='livres-papier'),
    path('livres-audio/', views.LivresAudioView.as_view(), name='livres-audio'),
    path('livre/<slug:slug>/', views.LivreDetailView.as_view(), name='livre-detail'),
    path('auteurs/', views.AuteursView.as_view(), name='auteurs'),
    path('auteur/<slug:slug>/', views.AuteurDetailView.as_view(), name='auteur-detail'),
    path('collection/<slug:slug>/', views.CollectionDetailView.as_view(), name='collection-detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('a-propos/', views.AProposView.as_view(), name='a-propos'),
    path('nos-contrats/', views.NosContratsView.as_view(), name='nos-contrats'),
    path('soumettre-manuscrit/', views.SoumissionManuscritView.as_view(), name='soumission-manuscrit'),
    path('actualites/', views.ActualitesView.as_view(), name='actualites'),
    path('actualite/<slug:slug>/', views.ActualiteDetailView.as_view(), name='actualite-detail'),
    path('conversion-texte-audio/', views.AudioConversionView.as_view(), name='conversion-audio'),
    path('conversion-texte-audio/payer/<int:demande_id>/', views.conversion_payment_redirect, name='conversion-audio-pay'),
    path('compte/connexion/', views.LoginView.as_view(), name='login'),
    path('compte/deconnexion/', auth_views.LogoutView.as_view(next_page='catalogue:conversion-audio'), name='logout'),
    path('compte/creer/', views.SignupView.as_view(), name='signup'),
    path('compte/activation/<uidb64>/<token>/', views.activate_account, name='activate'),
    path(
        'compte/mot-de-passe/',
        views.PasswordResetView.as_view(
            success_url=reverse_lazy('catalogue:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'compte/mot-de-passe/envoye/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'compte/mot-de-passe/confirmation/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('catalogue:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'compte/mot-de-passe/termine/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
    path('recherche/', views.SearchView.as_view(), name='search'),
    path('mentions-legales/', views.LegalView.as_view(), name='mentions-legales'),
    path('confidentialite/', views.LegalView.as_view(), name='confidentialite'),
    path('cookies/', views.LegalView.as_view(), name='cookies'),
    path('page/<slug:slug>/', views.PageDetailView.as_view(), name='page-detail'),
    
    # Formulaires
    path('newsletter/inscription/', views.inscription_newsletter, name='inscription-newsletter'),
    path('contact/submit/', views.contact_submit, name='contact-submit'),
    
    # API JSON
    path('api/livres/', views.livres_json, name='livres-json'),
    path('api/auteurs/', views.auteurs_json, name='auteurs-json'),
    path('api/livre/<int:livre_id>/', views.livre_detail_json, name='livre-detail-json'),
]
