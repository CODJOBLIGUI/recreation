# ===============================================================================
# SECTION 1 : MODÈLES DE BASE (CORE)
# Emplacement : apps/core/models.py
# ===============================================================================

"""
Modèles abstraits réutilisables pour tout le projet.
Ces modèles de base permettent d'éviter la répétition de code.
"""

from django.db import models
from django.utils.text import slugify

class TimeStampedModel(models.Model):
    """
    Modèle abstrait qui ajoute des timestamps automatiques.
    À utiliser comme classe de base pour tous les modèles qui ont besoin
    de savoir quand ils ont été créés et modifiés.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        db_index=True  # Index pour améliorer les performances des requêtes
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    class Meta:
        abstract = True  # Ce modèle ne créera pas de table en BDD


class SEOModel(models.Model):
    """
    Modèle abstrait pour les champs SEO (référencement).
    Ajoute des méta-données pour optimiser le référencement des pages.
    """
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Titre SEO",
        help_text="Titre optimisé pour les moteurs de recherche (max 60 caractères)"
    )
    meta_description = models.TextField(
        max_length=160,
        blank=True,
        verbose_name="Description SEO",
        help_text="Description pour les moteurs de recherche (max 160 caractères)"
    )
    
    class Meta:
        abstract = True


class SiteAppearance(models.Model):
    """
    Apparence globale du site.
    """

    site_name = models.CharField(max_length=120, default="Editions Recréation", verbose_name="Nom du site")
    logo = models.ImageField(upload_to="branding/%Y/%m/", blank=True, null=True, verbose_name="Logo")
    favicon = models.ImageField(upload_to="branding/%Y/%m/", blank=True, null=True, verbose_name="Favicon")
    audio_human_hero_image = models.ImageField(
        upload_to="branding/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Image hero bleu (gauche)",
    )

    primary_color = models.CharField(max_length=20, default="#F5F1E8", verbose_name="Couleur primaire")
    accent_color = models.CharField(max_length=20, default="#0A18FF", verbose_name="Couleur accent")
    accent_dark = models.CharField(max_length=20, default="#001FD8", verbose_name="Couleur accent foncée")
    text_color = models.CharField(max_length=20, default="#2C2C2C", verbose_name="Couleur texte")
    text_light = models.CharField(max_length=20, default="#4A4A4A", verbose_name="Couleur texte secondaire")
    light_bg = models.CharField(max_length=20, default="#F9F7F3", verbose_name="Fond clair")
    dark_bg = models.CharField(max_length=20, default="#2C2C2C", verbose_name="Fond foncé")

    font_heading = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Police titres",
        help_text="Ex: 'Cormorant Garamond', serif",
    )
    font_body = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Police texte",
        help_text="Ex: 'Source Serif 4', serif",
    )

    instagram = models.URLField(blank=True, verbose_name="Instagram")
    facebook = models.URLField(blank=True, verbose_name="Facebook")
    x_twitter = models.URLField(blank=True, verbose_name="X (Twitter)")
    tiktok = models.URLField(blank=True, verbose_name="TikTok")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")
    youtube = models.URLField(blank=True, verbose_name="YouTube")
    whatsapp = models.URLField(blank=True, verbose_name="WhatsApp")
    audio_payment_url = models.URLField(blank=True, verbose_name="Lien de paiement (conversion texte en audio)")
    site_email = models.EmailField(blank=True, verbose_name="Email de la maison d'édition")
    audio_payment_url_0 = models.URLField(blank=True, verbose_name="Paiement audio (1 à 50 pages)")
    audio_payment_url_1 = models.URLField(blank=True, verbose_name="Paiement audio (1 à 100 pages)")
    audio_payment_url_2 = models.URLField(blank=True, verbose_name="Paiement audio (101 à 200 pages)")
    audio_payment_url_3 = models.URLField(blank=True, verbose_name="Paiement audio (201 à 500 pages)")
    audio_payment_url_4 = models.URLField(blank=True, verbose_name="Paiement audio (501 à 1000 pages)")
    audio_payment_url_5 = models.URLField(blank=True, verbose_name="Paiement audio (1001+ pages)")
    audio_human_payment_url = models.URLField(blank=True, verbose_name="Lien paiement (lecture par un humain)")
    audio_human_payment_url_male = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (voix masculine)")
    audio_human_payment_url_female = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (voix féminine)")
    audio_human_payment_url_0 = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (1 à 50 pages)")
    audio_human_payment_url_1 = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (1 à 100 pages)")
    audio_human_payment_url_2 = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (101 à 200 pages)")
    audio_human_payment_url_3 = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (201 à 500 pages)")
    audio_human_payment_url_4 = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (501 à 1000 pages)")
    audio_human_payment_url_5 = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (1001+ pages)")
    footer_copyright = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Mention de copyright (footer)",
        help_text="Utilisez {year} pour l'année automatique.",
    )

    class Meta:
        verbose_name = "Apparence du site"
        verbose_name_plural = "Apparence du site"

    def __str__(self):
        return self.site_name
