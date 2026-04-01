# ===============================================================================

"""
Modèles abstraits réutilisables pour tout le projet.
Ces modèles de base permettent d'éviter la répétition de code.
"""

from django.db import models
from django.utils.text import slugify
from html import unescape


def _normalize_text_value(value):
    if value is None:
        return value
    if not isinstance(value, str):
        return value
    text = unescape(value)
    replacements = {
        "ÃƒÂ©": "é",
        "ÃƒÂ¨": "è",
        "ÃƒÂª": "ê",
        "ÃƒÂ«": "ë",
        "ÃƒÂ ": "à",
        "ÃƒÂ¢": "â",
        "ÃƒÂ®": "î",
        "ÃƒÂ´": "ô",
        "ÃƒÂ¹": "ù",
        "ÃƒÂ»": "û",
        "ÃƒÂ§": "ç",
        "Ãƒâ€°": "É",
        "Ãƒâ‚¬": "À",
        "Ã¢â‚¬â„¢": "’",
        "Ã¢â‚¬Å“": "“",
        "Ã¢â‚¬Â": "”",
        "Ã¢â‚¬â€œ": "–",
        "Ã¢â‚¬â€": "—",
        "Ã‚": "",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text

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

    def save(self, *args, **kwargs):
        # Nettoie automatiquement les textes pour éviter les caractères corrompus
        for field in self._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):
                if isinstance(field, (models.EmailField, models.URLField, models.SlugField)):
                    continue
                value = getattr(self, field.name, None)
                if isinstance(value, str) and value:
                    cleaned = _normalize_text_value(value)
                    if cleaned != value:
                        setattr(self, field.name, cleaned)
        super().save(*args, **kwargs)


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
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Mots-clés SEO",
        help_text="Mots-clés séparés par des virgules (max 255 caractères)",
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
    audio_payment_url_1 = models.URLField(blank=True, verbose_name="Paiement audio (1 à 50 pages)")
    audio_payment_url_2 = models.URLField(blank=True, verbose_name="Paiement audio (51 à 100 pages)")
    audio_payment_url_3 = models.URLField(blank=True, verbose_name="Paiement audio (101 à 200 pages)")
    audio_payment_url_4 = models.URLField(blank=True, verbose_name="Paiement audio (201 à 500 pages)")
    audio_payment_url_5 = models.URLField(blank=True, verbose_name="Paiement audio (501+ pages)")
    audio_human_payment_url = models.URLField(blank=True, verbose_name="Lien de paiement (voix humaine)")
    audio_human_payment_url_1 = models.URLField(blank=True, verbose_name="Paiement voix humaine (1 à 50 pages)")
    audio_human_payment_url_2 = models.URLField(blank=True, verbose_name="Paiement voix humaine (51 à 100 pages)")
    audio_human_payment_url_3 = models.URLField(blank=True, verbose_name="Paiement voix humaine (101 à 200 pages)")
    audio_human_payment_url_4 = models.URLField(blank=True, verbose_name="Paiement voix humaine (201 à 500 pages)")
    audio_human_payment_url_5 = models.URLField(blank=True, verbose_name="Paiement voix humaine (501 à 1000 pages)")
    audio_human_payment_url_6 = models.URLField(blank=True, verbose_name="Paiement voix humaine (1001+ pages)")

    tts_use_normalization = models.BooleanField(
        default=True,
        verbose_name="Activer la normalisation TTS",
        help_text="Active la normalisation automatique des sigles et des MAJUSCULES avant conversion audio.",
    )
    tts_acronyms = models.TextField(
        blank=True,
        verbose_name="Dictionnaire sigles (TTS)",
        help_text=(
            "Une entrée par ligne. Format: SIGLE=prononciation. "
            "Ex: UNESCO=unésco. Si pas de valeur, le sigle sera épelé."
        ),
    )
    site_meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Mots-clés SEO (site)",
        help_text="Mots-clés séparés par des virgules pour le site",
    )

    tts_spell_unknown = models.BooleanField(
        default=True,
        verbose_name="Épeler les sigles inconnus",
        help_text="Si activé, les sigles inconnus (2-4 lettres) sont épelés.",
    )

    class Meta:
        verbose_name = "Apparence du site"
        verbose_name_plural = "Apparence du site"

    def __str__(self):
        return self.site_name


class SiteContent(TimeStampedModel):
    """Textes et labels éditables du site (singleton)."""

    header_search_placeholder = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Placeholder recherche",
        default="Rechercher des livres, auteurs, actualités...",
    )
    header_search_button = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Bouton recherche",
        default="Chercher",
    )
    newsletter_placeholder = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Placeholder newsletter",
        default="Votre email",
    )
    newsletter_button_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Bouton newsletter",
        default="Bulletin",
    )
    nav_menu_label = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Label bouton menu",
        default="Menu",
    )
    nav_drawer_title = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Titre menu mobile",
        default="Menu",
    )
    nav_drawer_social_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre réseaux sociaux (mobile)",
        default="Suivez Recréation sur les réseaux sociaux",
    )
    nav_drawer_shop_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Label shop (mobile)",
        default="Recréation Shop",
    )
    nav_cta_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre CTA menu",
        default="Abonnez-vous à la newsletter",
    )
    nav_cta_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Texte CTA menu",
        default="Recevez nos actualités et nouveautés.",
    )
    nav_cta_button = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Bouton CTA menu",
        default="S'abonner",
    )
    footer_slogan = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Slogan footer",
        default="Avec le verbe, recréons le monde et conservons en une copie dans un livre !",
    )
    footer_address = models.CharField(
        max_length=240,
        blank=True,
        verbose_name="Adresse footer",
        default="Bénin | Abomey-Calavi, France | Marseille, avec des Représentants éditoriaux dans 7 autres pays en Afrique.",
    )
    footer_action_phone_label = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Label action téléphone",
        default="Téléphone",
    )
    footer_action_submit_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Label action soumission",
        default="Soumettre un manuscrit",
    )
    footer_action_email_label = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Label action email",
        default="E-mail",
    )
    footer_social_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre réseaux sociaux (footer)",
        default="Nous suivre les réseaux sociaux",
    )
    footer_catalogue_title = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Titre colonne Catalogue",
        default="Catalogue",
    )
    footer_collections_title = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Titre collections",
        default="Collections",
    )
    footer_audio_cta_label = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="CTA audio",
        default="Conversion de texte en audio",
    )
    footer_shop_cta_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="CTA shop",
        default="Recréation Shop",
    )
    footer_resources_title = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Titre colonne Ressources",
        default="Ressources",
    )
    footer_contact_link_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Lien Nous contacter",
        default="Nous contacter",
    )
    footer_copyright_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Copyright",
        default="Editions Recréation - Tous droits réservés - 2026",
    )
    default_meta_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Meta title par défaut",
        default="Editions Recréation - Maison d'édition généraliste",
    )
    default_meta_description = models.TextField(
        max_length=200,
        blank=True,
        verbose_name="Meta description par défaut",
        default="Editions Recréation, maison d'édition généraliste. Découvrez nos livres papier, numériques et audio.",
    )
    default_meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta keywords par défaut",
        default="",
        help_text="Mots-clés séparés par des virgules",
    )
    home_meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta keywords Accueil",
        default="",
    )
    contact_meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta keywords Contact",
        default="",
    )
    catalogue_meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta keywords Catalogue",
        default="",
    )
    actualites_meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta keywords Actualités",
        default="",
    )
    auteurs_meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta keywords Auteurs",
        default="",
    )
    a_propos_meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta keywords A propos",
        default="",
    )
    nos_contrats_meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta keywords Nos contrats",
        default="",
    )
    soumission_meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta keywords Soumission manuscrit",
        default="",
    )
    conversion_meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta keywords Conversion audio",
        default="",
    )
    committee_login_brand_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Comite - Titre marque",
        default="Editions Recreation",
    )
    committee_login_brand_subtitle = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Comite - Sous-titre marque",
        default="Membres du Comite de lecture",
    )
    committee_login_title = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Comite - Titre connexion",
        default="Connexion",
    )
    committee_login_text_primary = models.CharField(
        max_length=220,
        blank=True,
        verbose_name="Comite - Texte connexion 1",
        default="Connectez-vous pour acceder a l'espace des membres du Comite de lecture.",
    )
    committee_login_text_secondary = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Comite - Texte connexion 2",
        default="Si vous n'avez pas encore un compte evaluateur, inscrivez-vous.",
    )
    committee_signup_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Comite - Titre inscription",
        default="Inscription evaluateur",
    )
    committee_signup_intro = models.TextField(
        blank=True,
        verbose_name="Comite - Introduction inscription",
        default="Veuillez completer ce formulaire afin de soumettre votre demande d'acces. Votre demande fera l'objet d'une analyse par un administrateur. Une fois la conformite de votre profil a nos criteres validee, votre compte sera active.",
    )
    committee_signup_confidentiality_text = models.TextField(
        blank=True,
        verbose_name="Comite - Texte confidentialite",
        default="Votre inscription implique votre accord pour garantir la confidentialite des donnees personnelles de nos auteurs et de tous les fichiers dont vous auriez connaissance, afin d'empecher toute divulgation a des tiers. Les fichiers telecharges lors de l'evaluation des dossiers d'edition ne doivent en aucun cas etre conserves. La suppression est imperative dans un delai inferieur a une semaine. Prenez-vous acte de ces dispositions et consentez-vous a en respecter strictement toutes les clauses ?",
    )
    committee_signup_motivation_label = models.CharField(
        max_length=220,
        blank=True,
        verbose_name="Comite - Question motivation",
        default="Qu'est-ce qui vous motive a rejoindre l'equipe des membres du Comite de lecture des editions Recreation ?",
    )
    committee_signup_unpaid_label = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Comite - Question mission non remuneree",
        default="Cette mission n'est pas remuneree. En avez-vous conscience et etes-vous toujours partant pour nous rejoindre ?",
    )
    committee_signup_submit_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Comité - Bouton inscription",
        default="Envoyer la demande",
    )
    nav_brand_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Nom affiché menu",
        default="Recréation",
    )
    nav_drawer_collections_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre collections (menu mobile)",
        default="Collections",
    )
    nav_drawer_formats_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre formats (menu mobile)",
        default="Autres versions de livres",
    )
    nav_drawer_services_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre services (menu mobile)",
        default="Autres services",
    )
    nav_drawer_books_digital_label = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Lien livres numeriques (menu mobile)",
        default="Livres numériques",
    )
    nav_drawer_books_audio_label = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Lien livres audio (menu mobile)",
        default="Livres audio",
    )
    nav_drawer_books_print_label = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Lien livres papier (menu mobile)",
        default="Livres papier",
    )
    nav_drawer_conversion_label = models.CharField(
        max_length=180,
        blank=True,
        verbose_name="Lien conversion audio (menu mobile)",
        default="Conversion de texte en audio",
    )
    nav_drawer_committee_label = models.CharField(
        max_length=220,
        blank=True,
        verbose_name="Lien comité lecture (menu mobile)",
        default="Espace des membres du Comité de lecture",
    )

    home_carousel_cta_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="CTA carrousel accueil",
        default="Découvrir",
    )
    home_section_nouveautes_title = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Titre section nouveautés",
        default="Nouveautés",
    )
    home_section_bestsellers_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre section meilleures ventes",
        default="Meilleures Ventes",
    )
    home_section_upcoming_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre section prochaines parutions",
        default="Prochaines Parutions",
    )
    home_section_news_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre section actualites accueil",
        default="Suivez l’actualité",
    )
    home_news_cta_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="CTA actualites accueil",
        default="Lire la suite",
    )
    home_newsletter_title = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Titre newsletter accueil",
        default="Restez informé de nos nouveautés",
    )
    home_newsletter_button_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Bouton newsletter accueil",
        default="S'abonner",
    )
    home_card_cta_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="CTA carte livre",
        default="Voir détails",
    )
    home_upcoming_cta_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="CTA prochaines parutions",
        default="Découvrir",
    )
    home_tabs_all = models.CharField(max_length=60, blank=True, verbose_name="Onglet Toutes", default="Toutes")
    home_tabs_roman = models.CharField(max_length=60, blank=True, verbose_name="Onglet Romans", default="Romans")
    home_tabs_poemes = models.CharField(max_length=60, blank=True, verbose_name="Onglet Poemes", default="Poèmes")
    home_tabs_essai = models.CharField(max_length=60, blank=True, verbose_name="Onglet Essais", default="Essais")
    home_tabs_polars = models.CharField(max_length=80, blank=True, verbose_name="Onglet Polars", default="Polars/Thrillers")
    home_tabs_bd = models.CharField(max_length=40, blank=True, verbose_name="Onglet BD", default="BD")
    home_tabs_theatres = models.CharField(max_length=60, blank=True, verbose_name="Onglet Theatres", default="Théâtres")
    home_tabs_nouvelles = models.CharField(max_length=60, blank=True, verbose_name="Onglet Nouvelles", default="Nouvelles")
    catalogue_page_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre catalogue",
        default="Notre Catalogue",
    )
    catalogue_page_subtitle = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Sous-titre catalogue",
        default="Découvrez tous nos livres",
    )
    catalogue_search_placeholder = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Placeholder recherche catalogue",
        default="Rechercher un livre, auteur...",
    )
    catalogue_search_button_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Bouton recherche catalogue",
        default="Rechercher",
    )

    actualites_page_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre actualites",
        default="Actualités",
    )
    actualites_page_subtitle = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Sous-titre actualites",
        default="Découvrez nos actualités et nos événements du moment.",
    )
    actualites_read_more_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="CTA actualites",
        default="Lire la suite",
    )
    actualites_filter_apply_label = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Bouton appliquer actualites",
        default="Appliquer",
    )
    actualites_filter_reset_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Bouton reinitialiser actualites",
        default="Réinitialiser",
    )
    actualites_filter_type_label = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Label type actualites",
        default="Type d’actualités",
    )
    actualites_filter_year_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Label annee actualites",
        default="Année",
    )
    actualites_filter_month_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Label mois actualites",
        default="Mois",
    )

    auteurs_page_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre auteurs",
        default="Nos Auteurs",
    )
    auteurs_page_subtitle = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Sous-titre auteurs",
        default="Découvrez les plumes élues au sein de notre maison",
    )
    auteurs_filter_button_label = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Bouton filtre auteurs",
        default="Filtrer",
    )
    auteurs_filter_placeholder = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Placeholder filtre auteurs",
        default="Toutes les nationalités",
    )
    auteurs_card_cta_label = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="CTA auteurs",
        default="Voir la bibliographie",
    )

    contact_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre contact",
        default="Contactez-nous",
    )
    contact_subtitle = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Sous-titre contact",
        default="Une question ? Un projet ? N'hésitez pas à nous contacter.",
    )
    contact_address_label = models.CharField(max_length=80, blank=True, verbose_name="Label adresse", default="Adresse")
    contact_phone_label = models.CharField(max_length=80, blank=True, verbose_name="Label telephone", default="Telephone")
    contact_email_label = models.CharField(max_length=80, blank=True, verbose_name="Label email", default="Email")
    contact_address_text = models.CharField(
        max_length=240,
        blank=True,
        verbose_name="Adresse contact",
        default="Bénin | Abomey-Calavi, France | Marseille, avec des Représentants éditoriaux dans 7 autres pays en Afrique.",
    )
    contact_phone_display = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Téléphone affiche",
        default="(+229) 01 68 80 97 77",
    )
    contact_phone_link = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Telephone lien",
        default="+22901688097777",
    )
    contact_email_value = models.EmailField(
        max_length=120,
        blank=True,
        verbose_name="Email contact",
        default="contactedrecreation@gmail.com",
    )
    contact_form_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre formulaire contact",
        default="Envoyez-nous un message",
    )
    contact_submit_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Bouton contact",
        default="Envoyer le message",
    )

    newsletter_message_success = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Newsletter - succès",
        default="Merci ! Vous êtes inscrit à notre newsletter.",
    )
    newsletter_message_reactivated = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Newsletter - réactivation",
        default="Votre inscription a été réactivée.",
    )
    newsletter_message_already = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Newsletter - déjà inscrit",
        default="Vous êtes déjà inscrit.",
    )
    newsletter_message_error = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Newsletter - erreur",
        default="Une erreur s'est produite. Veuillez vérifier votre email.",
    )
    newsletter_message_invalid = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Newsletter - email invalide",
        default="Veuillez saisir une adresse email valide.",
    )
    contact_message_success = models.CharField(
        max_length=240,
        blank=True,
        verbose_name="Contact - succès",
        default="Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.",
    )
    contact_message_error = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Contact - erreur",
        default="Une erreur s'est produite. Veuillez vérifier les informations saisies.",
    )
    contact_message_missing = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Contact - champs manquants",
        default="Veuillez remplir tous les champs obligatoires.",
    )
    soumission_message_success = models.CharField(
        max_length=240,
        blank=True,
        verbose_name="Soumission - succès",
        default="Merci ! Votre manuscrit a été soumis avec succès. Nous vous contacterons rapidement.",
    )
    soumission_message_error = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Soumission - erreur",
        default="Une erreur s'est produite. Veuillez vérifier les informations saisies.",
    )
    committee_signup_success = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Comité - demande envoyée",
        default="Votre demande a été envoyée. Un administrateur doit l’approuver.",
    )
    committee_review_saved = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Comité - évaluation enregistrée",
        default="Évaluation enregistrée.",
    )
    audio_message_success = models.CharField(
        max_length=260,
        blank=True,
        verbose_name="Audio - prêt",
        default="Votre audio est prêt. Vous pouvez l'écouter en cliquant sur play. Vous pouvez aussi le télécharger gratuitement.",
    )
    audio_message_failed = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Audio - échec",
        default="La génération de l’audio a échoué. Veuillez réessayer.",
    )
    audio_message_not_ready = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Audio - non abouti",
        default="La génération de l’audio n’a pas abouti. Veuillez réessayer.",
    )
    audio_payment_pending_message = models.CharField(
        max_length=240,
        blank=True,
        verbose_name="Audio - paiement à vérifier",
        default="Merci. Nous allons vérifier votre paiement et vous contacter très rapidement par e-mail.",
    )
    account_signup_success = models.CharField(
        max_length=240,
        blank=True,
        verbose_name="Compte - création",
        default="Compte créé. Un email de confirmation vous a été envoyé. Activez votre compte pour continuer.",
    )
    account_activation_success = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Compte - activation ok",
        default="Votre compte est activé. Vous pouvez utiliser le service.",
    )
    account_activation_invalid = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Compte - activation invalide",
        default="Lien d’activation invalide ou expiré.",
    )
    account_login_invalid = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Compte - identifiants invalides",
        default="Identifiants invalides.",
    )

    footer_link_catalogue = models.CharField(max_length=80, blank=True, verbose_name="Lien catalogue", default="Catalogue")
    footer_link_livres_numeriques = models.CharField(max_length=120, blank=True, verbose_name="Lien livres numeriques", default="Livres numériques")
    footer_link_livres_audio = models.CharField(max_length=120, blank=True, verbose_name="Lien livres audio", default="Livres audio")
    footer_link_livres_papier = models.CharField(max_length=120, blank=True, verbose_name="Lien livres papier", default="Livres papier")
    footer_link_actualites = models.CharField(max_length=80, blank=True, verbose_name="Lien actualites", default="Actualités")
    footer_link_auteurs = models.CharField(max_length=80, blank=True, verbose_name="Lien auteurs", default="Auteurs")
    footer_link_a_propos = models.CharField(max_length=80, blank=True, verbose_name="Lien a propos", default="A propos")
    footer_link_nouveautes = models.CharField(max_length=80, blank=True, verbose_name="Lien nouveautes", default="Nouveautés")
    footer_link_a_paraitre = models.CharField(max_length=80, blank=True, verbose_name="Lien a paraitre", default="A paraître")
    footer_link_meilleures_ventes = models.CharField(max_length=120, blank=True, verbose_name="Lien meilleures ventes", default="Meilleures ventes")
    footer_link_nos_contrats = models.CharField(max_length=80, blank=True, verbose_name="Lien nos contrats", default="Nos contrats")
    footer_link_equipe = models.CharField(max_length=80, blank=True, verbose_name="Lien equipe", default="Equipe")
    footer_link_devenir_auteur = models.CharField(max_length=120, blank=True, verbose_name="Lien devenir auteur", default="Devenir auteur")
    footer_link_rejoindre_comite = models.CharField(max_length=200, blank=True, verbose_name="Lien comité lecture", default="Rejoindre notre Comité de lecture")
    footer_link_mentions = models.CharField(max_length=120, blank=True, verbose_name="Lien mentions", default="Mentions legales")
    footer_link_confidentialite = models.CharField(max_length=120, blank=True, verbose_name="Lien confidentialité", default="Confidentialité")
    footer_link_cookies = models.CharField(max_length=80, blank=True, verbose_name="Lien cookies", default="Cookies")
    class Meta:
        verbose_name = "Contenu du site"
        verbose_name_plural = "Contenu du site"

    def __str__(self):
        return "Contenu du site"











