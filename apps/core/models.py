# ===============================================================================
# SECTION 1 : MODLES DE BASE (CORE)
# Emplacement : apps/core/models.py
# ===============================================================================

"""
Modles abstraits rutilisables pour tout le projet.
Ces modles de base permettent d?viter la rptition de code.
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
    accent_dark = models.CharField(max_length=20, default="#001FD8", verbose_name="Couleur accent fonce")
    text_color = models.CharField(max_length=20, default="#2C2C2C", verbose_name="Couleur texte")
    text_light = models.CharField(max_length=20, default="#4A4A4A", verbose_name="Couleur texte secondaire")
    light_bg = models.CharField(max_length=20, default="#F9F7F3", verbose_name="Fond clair")
    dark_bg = models.CharField(max_length=20, default="#2C2C2C", verbose_name="Fond fonc")

    font_heading = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Police titres",
        help_text="Ex: ?Cormorant Garamond?, serif",
    )
    font_body = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Police texte",
        help_text="Ex: ?Source Serif 4?, serif",
    )

    instagram = models.URLField(blank=True, verbose_name="Instagram")
    facebook = models.URLField(blank=True, verbose_name="Facebook")
    x_twitter = models.URLField(blank=True, verbose_name="X (Twitter)")
    tiktok = models.URLField(blank=True, verbose_name="TikTok")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")
    youtube = models.URLField(blank=True, verbose_name="YouTube")
    whatsapp = models.URLField(blank=True, verbose_name="WhatsApp")
    audio_payment_url = models.URLField(blank=True, verbose_name="Lien de paiement (conversion texte en audio)")
    site_email = models.EmailField(blank=True, verbose_name="Email de la maison d?dition")
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
        help_text="Utilisez {year} pour l?anne automatique.",
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
    Contenus globaux modifiables depuis l?admin.
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

    nav_title_collections = models.CharField(
        max_length=120,
        blank=True,
        default="Collections",
        verbose_name="Navigation - Titre collections",
    )
    nav_title_formats = models.CharField(
        max_length=120,
        blank=True,
        default="Autres versions de livres",
        verbose_name="Navigation - Titre formats",
    )
    nav_title_services = models.CharField(
        max_length=120,
        blank=True,
        default="Autres services",
        verbose_name="Navigation - Titre services",
    )
    nav_menu_label = models.CharField(
        max_length=80,
        blank=True,
        default="Menu",
        verbose_name="Navigation - Libelle bouton menu",
    )
    nav_cta_title = models.CharField(
        max_length=160,
        blank=True,
        default="Abonnez-vous a la newsletter",
        verbose_name="Navigation - Titre newsletter",
    )
    nav_cta_text = models.CharField(
        max_length=240,
        blank=True,
        default="Recevez nos actualites et nouveautes.",
        verbose_name="Navigation - Texte newsletter",
    )
    nav_cta_button = models.CharField(
        max_length=80,
        blank=True,
        default="S?abonner",
        verbose_name="Navigation - Bouton newsletter",
    )
    header_search_placeholder = models.CharField(
        max_length=160,
        blank=True,
        default="Rechercher livres, auteurs, actualites...",
        verbose_name="Header - Placeholder recherche",
    )
    header_search_button = models.CharField(
        max_length=80,
        blank=True,
        default="Rechercher",
        verbose_name="Header - Bouton recherche",
    )

    footer_title_catalogue = models.CharField(
        max_length=120,
        blank=True,
        default="Catalogue",
        verbose_name="Footer - Titre catalogue",
    )
    footer_title_collections = models.CharField(
        max_length=120,
        blank=True,
        default="Collections",
        verbose_name="Footer - Titre collections",
    )
    footer_title_resources = models.CharField(
        max_length=120,
        blank=True,
        default="Ressources",
        verbose_name="Footer - Titre ressources",
    )
    footer_title_services = models.CharField(
        max_length=120,
        blank=True,
        default="Services",
        verbose_name="Footer - Titre services",
    )
    footer_social_title = models.CharField(
        max_length=160,
        blank=True,
        default="Nous suivre les reseaux sociaux",
        verbose_name="Footer - Titre reseaux sociaux",
    )
    footer_catalogue_label = models.CharField(
        max_length=120,
        blank=True,
        default="Catalogue",
        verbose_name="Footer - Libelle catalogue",
    )
    footer_catalogue_news_label = models.CharField(
        max_length=120,
        blank=True,
        default="Nouveautes",
        verbose_name="Footer - Libelle nouveautes",
    )
    footer_catalogue_upcoming_label = models.CharField(
        max_length=120,
        blank=True,
        default="Prochaines parutions",
        verbose_name="Footer - Libelle prochaines parutions",
    )
    footer_action_phone_label = models.CharField(
        max_length=120,
        blank=True,
        default="Telephone",
        verbose_name="Footer - Libelle telephone",
    )
    footer_action_submit_label = models.CharField(
        max_length=160,
        blank=True,
        default="Soumettez votre manuscrit/tapuscrit",
        verbose_name="Footer - Libelle soumission",
    )
    footer_action_email_label = models.CharField(
        max_length=120,
        blank=True,
        default="E-mail",
        verbose_name="Footer - Libelle email",
    )
    footer_action_conversion_label = models.CharField(
        max_length=160,
        blank=True,
        default="Conversion de texte en audio",
        verbose_name="Footer - Libelle conversion audio",
    )
    footer_action_shop_label = models.CharField(
        max_length=120,
        blank=True,
        default="Recreation Shop",
        verbose_name="Footer - Libelle boutique",
    )

    conversion_hero_note = models.TextField(
        blank=True,
        default=(
            "Collez votre texte ou televersez un fichier. Le service est gratuit "
            "pour les textes de 5000 caracteres maximum. Les fichiers televerses "
            "sont systematiquement soumis au paiement. Apres paiement, nous produisons "
            "l?audio et vous l?envoyons par e-mail."
        ),
        verbose_name="Conversion - Texte d?introduction",
    )
    conversion_free_limit_text = models.CharField(
        max_length=200,
        blank=True,
        default="Le service est gratuit pour les textes de 5000 caracteres maximum.",
        verbose_name="Conversion - Message limite gratuite",
    )
    conversion_file_payment_text = models.CharField(
        max_length=200,
        blank=True,
        default="Les fichiers televerses sont systematiquement soumis au paiement.",
        verbose_name="Conversion - Message fichier payant",
    )
    conversion_formats_text = models.CharField(
        max_length=200,
        blank=True,
        default="Formats pris en charge : txt, docx, pdf, jpg, png, pptx, xlsx, epub.",
        verbose_name="Conversion - Message formats",
    )
    conversion_form_title = models.CharField(
        max_length=160,
        blank=True,
        default="Convertissez votre texte ici",
        verbose_name="Conversion - Titre formulaire",
    )
    conversion_payment_note_text = models.CharField(
        max_length=200,
        blank=True,
        default="Le texte depasse la longueur autorisee en mode gratuit : payez un montant forfaitaire pour ce service.",
        verbose_name="Conversion - Note paiement",
    )
    conversion_payment_required_title = models.CharField(
        max_length=160,
        blank=True,
        default="Paiement requis",
        verbose_name="Conversion - Titre paiement requis",
    )
    conversion_payment_required_text = models.CharField(
        max_length=240,
        blank=True,
        default="Votre demande a ete enregistree. Veuillez proceder au paiement pour recevoir l?audio par e-mail.",
        verbose_name="Conversion - Texte paiement requis",
    )
    conversion_payment_error_text = models.CharField(
        max_length=200,
        blank=True,
        default="Impossible de lancer le paiement. Veuillez reessayer ou nous contacter.",
        verbose_name="Conversion - Erreur paiement",
    )
    conversion_processing_title = models.CharField(
        max_length=160,
        blank=True,
        default="Votre demande est en cours de traitement",
        verbose_name="Conversion - Titre traitement",
    )
    conversion_processing_text = models.CharField(
        max_length=200,
        blank=True,
        default="Nos equipes verifieront l?effectivite du paiement et vous feront un retour.",
        verbose_name="Conversion - Texte traitement",
    )
    conversion_progress_title = models.CharField(
        max_length=160,
        blank=True,
        default="Conversion en cours",
        verbose_name="Conversion - Titre progression",
    )
    conversion_progress_text = models.CharField(
        max_length=200,
        blank=True,
        default="Votre audio est en preparation. Cette page se mettra a jour automatiquement.",
        verbose_name="Conversion - Texte progression",
    )
    conversion_audio_ready_title = models.CharField(
        max_length=160,
        blank=True,
        default="Votre audio est pret",
        verbose_name="Conversion - Titre audio pret",
    )
    conversion_audio_download_label = models.CharField(
        max_length=160,
        blank=True,
        default="Telecharger l?audio (MP3)",
        verbose_name="Conversion - Bouton telechargement",
    )
    conversion_unavailable_free_text = models.CharField(
        max_length=240,
        blank=True,
        default="Service momentanement indisponible. Veuillez reessayer plus tard ou essayez avec une version payante.",
        verbose_name="Conversion - Indisponibilite gratuite",
    )
    conversion_unavailable_paid_text = models.CharField(
        max_length=240,
        blank=True,
        default="Le service payant est momentanement indisponible. Essayez un depot de fichiers ou la lecture par un humain.",
        verbose_name="Conversion - Indisponibilite payante",
    )
    conversion_free_limit_reached_text = models.CharField(
        max_length=240,
        blank=True,
        default="Vous avez atteint la limite de conversion gratuite quotidienne.",
        verbose_name="Conversion - Limite gratuite atteinte",
    )
    conversion_limit_cta_paid_label = models.CharField(
        max_length=160,
        blank=True,
        default="Essayer la version payante",
        verbose_name="Conversion - Bouton version payante",
    )
    conversion_limit_cta_human_label = models.CharField(
        max_length=160,
        blank=True,
        default="Lecture par un humain",
        verbose_name="Conversion - Bouton lecture humaine",
    )

    conversion_choice_title = models.CharField(
        max_length=160,
        blank=True,
        default="Conversion de texte en audio",
        verbose_name="Choix conversion - Titre",
    )
    conversion_choice_subtitle = models.CharField(
        max_length=240,
        blank=True,
        default="Choisissez le type de conversion qui vous convient : synthetique ou lecture humaine.",
        verbose_name="Choix conversion - Sous-titre",
    )
    conversion_choice_synth_title = models.CharField(
        max_length=160,
        blank=True,
        default="Conversion synthetique",
        verbose_name="Choix conversion - Titre synthetique",
    )
    conversion_choice_synth_text = models.CharField(
        max_length=240,
        blank=True,
        default="Conversion rapide par voix synthetique, gratuite jusqu?a 5000 caracteres.",
        verbose_name="Choix conversion - Texte synthetique",
    )
    conversion_choice_synth_button = models.CharField(
        max_length=160,
        blank=True,
        default="Continuer en synthetique",
        verbose_name="Choix conversion - Bouton synthetique",
    )
    conversion_choice_human_title = models.CharField(
        max_length=160,
        blank=True,
        default="Lecture par un humain",
        verbose_name="Choix conversion - Titre humain",
    )
    conversion_choice_human_text = models.CharField(
        max_length=240,
        blank=True,
        default="Confiez votre texte a un membre de notre equipe pour une lecture par un humain.",
        verbose_name="Choix conversion - Texte humain",
    )
    conversion_choice_human_button = models.CharField(
        max_length=200,
        blank=True,
        default="Continuer en lecture par un humain",
        verbose_name="Choix conversion - Bouton humain",
    )

    activation_email_subject = models.CharField(
        max_length=160,
        blank=True,
        default="Confirmez votre compte",
        verbose_name="Email - Sujet activation",
    )
    activation_email_body = models.TextField(
        blank=True,
        default=(
            "Bonjour {first_name},\n\n"
            "Merci de confirmer votre compte en cliquant sur ce lien :\n"
            "{activation_link}\n\n"
            "Editions Recreation"
        ),
        verbose_name="Email - Corps activation",
    )
    activation_success_message = models.CharField(
        max_length=200,
        blank=True,
        default="Votre compte est active. Vous pouvez utiliser le service.",
        verbose_name="Message - Activation reussie",
    )
    activation_invalid_message = models.CharField(
        max_length=200,
        blank=True,
        default="Lien d?activation invalide ou expire.",
        verbose_name="Message - Activation invalide",
    )
    signup_success_message = models.CharField(
        max_length=240,
        blank=True,
        default="Compte cree. Un email de confirmation vous a ete envoye. Activez votre compte pour continuer.",
        verbose_name="Message - Inscription reussie",
    )

    error_404_title = models.CharField(
        max_length=160,
        blank=True,
        default="Page introuvable",
        verbose_name="Erreur 404 - Titre",
    )
    error_404_text = models.TextField(
        blank=True,
        default="La page demandee est introuvable. Revenez a l?accueil ou utilisez la recherche.",
        verbose_name="Erreur 404 - Texte",
    )
    error_500_title = models.CharField(
        max_length=160,
        blank=True,
        default="Une erreur est survenue",
        verbose_name="Erreur 500 - Titre",
    )
    error_500_text = models.TextField(
        blank=True,
        default="Une erreur interne est survenue. Veuillez reessayer plus tard.",
        verbose_name="Erreur 500 - Texte",
    )

    class Meta:
        verbose_name = "Contenu du site"
        verbose_name_plural = "Contenus du site"

    def __str__(self):
        return "Contenus globaux"
