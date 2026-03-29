# ===============================================================================
# SECTION 1 : MODLES DE BASE (CORE)
# Emplacement : apps/core/models.py
# ===============================================================================

"""
Modles abstraits rutilisables pour tout le projet.
Ces modles de base permettent d'viter la rptition de code.
"""

from django.db import models
from django.utils.text import slugify

class TimeStampedModel(models.Model):
    """
    Modle abstrait qui ajoute des timestamps automatiques.
     utiliser comme classe de base pour tous les modles qui ont besoin
    de savoir quand ils ont t crs et modifis.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de cration",
        db_index=True  # Index pour amliorer les performances des requtes
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    class Meta:
        abstract = True  # Ce modle ne crera pas de table en BDD


class SEOModel(models.Model):
    """
    Modle abstrait pour les champs SEO (rfrencement).
    Ajoute des mta-donnes pour optimiser le rfrencement des pages.
    """
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Titre SEO",
        help_text="Titre optimis pour les moteurs de recherche (max 60 caractres)"
    )
    meta_description = models.TextField(
        max_length=160,
        blank=True,
        verbose_name="Description SEO",
        help_text="Description pour les moteurs de recherche (max 160 caractres)"
    )
    
    class Meta:
        abstract = True


class SiteAppearance(models.Model):
    """
    Apparence globale du site.
    """

    site_name = models.CharField(max_length=120, default="Editions Recration", verbose_name="Nom du site")
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
    accent_dark = models.CharField(max_length=20, default="#001FD8", verbose_name="Couleur accent fonce")
    text_color = models.CharField(max_length=20, default="#2C2C2C", verbose_name="Couleur texte")
    text_light = models.CharField(max_length=20, default="#4A4A4A", verbose_name="Couleur texte secondaire")
    light_bg = models.CharField(max_length=20, default="#F9F7F3", verbose_name="Fond clair")
    dark_bg = models.CharField(max_length=20, default="#2C2C2C", verbose_name="Fond fonc")

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
    site_email = models.EmailField(blank=True, verbose_name="Email de la maison d'dition")
    site_address = models.TextField(blank=True, verbose_name="Adresse (footer/contact)")
    site_legal_label = models.CharField(blank=True, max_length=120, verbose_name="Libell sige social (mentions lgales)")
    audio_payment_url_0 = models.URLField(blank=True, verbose_name="Paiement audio (1  50 pages)")
    audio_payment_url_1 = models.URLField(blank=True, verbose_name="Paiement audio (51  100 pages)")
    audio_payment_url_2 = models.URLField(blank=True, verbose_name="Paiement audio (101  200 pages)")
    audio_payment_url_3 = models.URLField(blank=True, verbose_name="Paiement audio (201  500 pages)")
    audio_payment_url_4 = models.URLField(blank=True, verbose_name="Paiement audio (501  1000 pages)")
    audio_payment_url_5 = models.URLField(blank=True, verbose_name="Paiement audio (1001+ pages)")
    audio_human_payment_url = models.URLField(blank=True, verbose_name="Lien paiement (lecture par un humain)")
    audio_human_payment_url_male = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (voix masculine)")
    audio_human_payment_url_female = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (voix fminine)")
    audio_human_payment_url_0 = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (1  50 pages)")
    audio_human_payment_url_1 = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (51  100 pages)")
    audio_human_payment_url_2 = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (101  200 pages)")
    audio_human_payment_url_3 = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (201  500 pages)")
    audio_human_payment_url_4 = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (501  1000 pages)")
    audio_human_payment_url_5 = models.URLField(blank=True, verbose_name="Paiement lecture par un humain (1001+ pages)")
    footer_copyright = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Mention de copyright (footer)",
        help_text="Utilisez {year} pour l'anne automatique.",
    )
    tts_acronyms = models.TextField(
        blank=True,
        verbose_name="Sigles TTS (separes par des virgules)",
        help_text="Ex: ONU, UE, USA, BTP",
    )

    class Meta:
        verbose_name = "Apparence du site"
        verbose_name_plural = "Apparence du site"

    def __str__(self):
        return self.site_name


class SiteContent(models.Model):
    """
    Contenus globaux modifiables depuis l'admin.
    """

    default_meta_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre SEO par defaut",
        help_text="Titre SEO utilise si une page ne definit pas son propre titre.",
    )
    default_meta_description = models.TextField(
        max_length=200,
        blank=True,
        verbose_name="Description SEO par defaut",
        help_text="Description SEO utilisee si une page ne definit pas sa propre description.",
    )
    default_canonical = models.URLField(
        blank=True,
        verbose_name="Canonical par defaut",
        help_text="URL canonical globale si une page ne definit pas la sienne.",
    )
    og_image = models.ImageField(
        upload_to="branding/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Image OpenGraph",
    )

    newsletter_title = models.CharField(
        max_length=160,
        blank=True,
        default="Abonnez-vous a la newsletter",
        verbose_name="Titre newsletter",
    )
    newsletter_subtitle = models.CharField(
        max_length=240,
        blank=True,
        default="Recevez nos actualites et nouveautes.",
        verbose_name="Sous-titre newsletter",
    )
    newsletter_placeholder = models.CharField(
        max_length=120,
        blank=True,
        default="Votre email",
        verbose_name="Placeholder newsletter",
    )
    newsletter_button_label = models.CharField(
        max_length=80,
        blank=True,
        default="Newsletter",
        verbose_name="Libelle bouton newsletter",
    )

    footer_slogan = models.TextField(
        blank=True,
        default="Avec le verbe, recreons le monde et conservons en une copie dans un livre !",
        verbose_name="Slogan pied de page",
    )
    footer_address = models.TextField(
        blank=True,
        default=(
            "Nous sommes au Benin, Abomey-Calavi et nous avons des representants "
            "editoriaux en France, Marseille et dans 7 autres pays en Afrique."
        ),
        verbose_name="Adresse pied de page",
    )
    footer_copyright = models.CharField(
        max_length=200,
        blank=True,
        default="Editions Recreation - Tous droits reserves",
        verbose_name="Mention copyright",
    )

    class Meta:
        verbose_name = "Contenu du site"
        verbose_name_plural = "Contenus du site"

    def __str__(self):
        return "Contenus globaux"
