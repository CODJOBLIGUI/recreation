"""
FICHIER : apps/catalogue/models.py
"""

from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import slugify
from apps.core.models import TimeStampedModel, SEOModel


# -------------------------------------------------------------------------------
# MANAGERS PERSONNALISÉS
# -------------------------------------------------------------------------------

class AuteurManager(models.Manager):
    """Manager pour Auteur."""
    
    def avec_livres(self):
        return self.prefetch_related("livres", "nationalites")
    
    def populaires(self):
        return self.annotate(
            nombre_livres=models.Count('livres')
        ).filter(nombre_livres__gt=0).order_by('-nombre_livres')


class LivreManager(models.Manager):
    """Manager pour Livre."""
    
    def nouveautes(self, limit=8):
        return self.filter(
            est_nouveau=True,
            est_publie=True
        ).prefetch_related('auteurs').order_by('-parution')[:limit]
    
    def bestsellers(self, limit=5):
        return self.filter(
            est_bestseller=True,
            est_publie=True
        ).prefetch_related('auteurs').order_by('-parution')[:limit]
    
    def prochaines_parutions(self, limit=6):
        return self.filter(
            est_prochaine_parution=True,
            est_publie=True
        ).prefetch_related('auteurs').order_by('parution')[:limit]
    
    def publies(self):
        return self.filter(est_publie=True)


# -------------------------------------------------------------------------------
# MODÈLE AUTEUR
# -------------------------------------------------------------------------------

class Nationalite(models.Model):
    """Modèle Nationalite."""

    nom = models.CharField(max_length=120, verbose_name="Nom du pays")
    code_iso = models.CharField(max_length=2, verbose_name="Code ISO (2 lettres)")
    drapeau = models.ImageField(
        upload_to="flags/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Drapeau (image)",
    )

    class Meta:
        verbose_name = "Nationalité"
        verbose_name_plural = "Nationalités"
        ordering = ["nom"]
        indexes = [models.Index(fields=["nom", "code_iso"])]

    def save(self, *args, **kwargs):
        if self.code_iso:
            self.code_iso = self.code_iso.upper()
        super().save(*args, **kwargs)

    def emoji(self):
        if not self.code_iso or len(self.code_iso) != 2:
            return ""
        return "".join(chr(127397 + ord(char)) for char in self.code_iso.upper())

    def __str__(self):
        return f"{self.nom} ({self.code_iso})" if self.code_iso else self.nom


class MenuLink(TimeStampedModel):
    """Modèle Lien de menu."""

    LOCATION_CHOICES = [
        ("header", "En-tête"),
        ("footer", "Pied de page"),
    ]

    title = models.CharField(max_length=100, verbose_name="Titre")
    url = models.CharField(max_length=300, verbose_name="URL")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    location = models.CharField(
        max_length=20,
        choices=LOCATION_CHOICES,
        default="header",
        verbose_name="Emplacement",
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Lien de menu"
        verbose_name_plural = "Liens de menu"
        ordering = ["location", "order", "title"]

    def __str__(self):
        return f"{self.title} ({self.location})"


class Page(TimeStampedModel, SEOModel):
    """Modèle Page."""

    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    hero_title = models.CharField(max_length=200, blank=True, verbose_name="Titre d'en-tête")
    hero_subtitle = models.CharField(max_length=255, blank=True, verbose_name="Sous-titre d'en-tête")
    hero_image = models.ImageField(
        upload_to="pages/heroes/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Image du hero",
        help_text="Image affichée dans le hero bleu de la page.",
    )
    body = RichTextField(verbose_name="Contenu")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    show_team = models.BooleanField(default=False, verbose_name="Afficher l'équipe")

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ["title"]

    def __str__(self):
        return self.title


class PageBlock(TimeStampedModel):
    """Bloc de page."""
    
    BLOCK_TYPES = [
        ("rich_text", "Texte libre"),
        ("image", "Image"),
        ("cta", "Appel à l'action"),
        ("grid", "Grille"),
        ("carousel", "Carrousel"),
        ("stats", "Statistiques"),
        ("team", "Équipe"),
        ("contact_form", "Formulaire de contact"),
        ("home_carousel", "Accueil - Carrousel"),
        ("home_nouveautes", "Accueil - Nouveautés"),
        ("home_bestsellers", "Accueil - Meilleures ventes"),
        ("home_parutions", "Accueil - Prochaines parutions"),
        ("home_actualites", "Accueil - Actualités"),
        ("home_newsletter", "Accueil - Newsletter"),
    ]
    
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="blocks",
        verbose_name="Page",
    )
    block_type = models.CharField(max_length=40, choices=BLOCK_TYPES, verbose_name="Type de bloc")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    titre = models.CharField(max_length=200, blank=True, verbose_name="Titre")
    sous_titre = models.CharField(max_length=255, blank=True, verbose_name="Sous-titre")
    contenu = RichTextField(blank=True, verbose_name="Contenu")
    image = models.ImageField(upload_to="pages/blocks/%Y/%m/", blank=True, null=True, verbose_name="Image")
    bouton_texte = models.CharField(max_length=120, blank=True, verbose_name="Texte du bouton")
    bouton_url = models.CharField(max_length=300, blank=True, verbose_name="URL du bouton")
    css_class = models.CharField(max_length=120, blank=True, verbose_name="Classe CSS")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Bloc de page"
        verbose_name_plural = "Blocs de page"
        ordering = ["ordre", "created_at"]
    
    def __str__(self):
        return f"{self.page.title} - {self.get_block_type_display()}"


class PageBlockItem(TimeStampedModel):
    """Élément d'un bloc (grille/carrousel)."""
    
    block = models.ForeignKey(
        PageBlock,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Bloc",
    )
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    titre = models.CharField(max_length=200, blank=True, verbose_name="Titre")
    sous_titre = models.CharField(max_length=255, blank=True, verbose_name="Sous-titre")
    contenu = RichTextField(blank=True, verbose_name="Contenu")
    image = models.ImageField(upload_to="pages/items/%Y/%m/", blank=True, null=True, verbose_name="Image")
    icone = models.CharField(max_length=80, blank=True, verbose_name="Classe d'icône (Font Awesome)")
    lien_texte = models.CharField(max_length=120, blank=True, verbose_name="Texte du lien")
    lien_url = models.CharField(max_length=300, blank=True, verbose_name="URL du lien")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Élément de bloc"
        verbose_name_plural = "Éléments de bloc"
        ordering = ["ordre", "created_at"]
    
    def __str__(self):
        return self.titre or f"Élément {self.pk}"


class Collection(TimeStampedModel, SEOModel):
    """Modèle Collection."""

    nom = models.CharField(max_length=150, verbose_name="Nom")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="Slug")
    description = RichTextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to="collections/%Y/%m/", blank=True, null=True, verbose_name="Image")
    ordre_affichage = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    est_active = models.BooleanField(default=True, verbose_name="Est active")

    class Meta:
        verbose_name = "Collection"
        verbose_name_plural = "Collections"
        ordering = ["ordre_affichage", "nom"]
        indexes = [models.Index(fields=["nom", "slug"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nom)
            slug = base_slug
            counter = 1
            while Collection.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse("catalogue:collection-detail", kwargs={"slug": self.slug})

class Auteur(TimeStampedModel, SEOModel):
    """Modèle Auteur."""
    
    nom = models.CharField(max_length=200, verbose_name="Nom complet", db_index=True)
    specialite = models.CharField(max_length=100, verbose_name="Spécialité")
    biographie = RichTextField(verbose_name="Biographie")
    photo = models.ImageField(upload_to='authors/%Y/%m/', verbose_name="Photo")
    slug = models.SlugField(max_length=250, unique=True, blank=True, verbose_name="Slug")
    nationalites = models.ManyToManyField(
        Nationalite,
        blank=True,
        related_name="auteurs",
        verbose_name="Nationalités",
        help_text="Selectionnez une ou plusieurs nationalites.",
    )
    
    objects = AuteurManager()
    
    class Meta:
        verbose_name = "Auteur"
        verbose_name_plural = "Auteurs"
        ordering = ['nom']
        indexes = [models.Index(fields=['nom'])]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nom)
            slug = base_slug
            counter = 1
            while Auteur.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nom
    
    def get_absolute_url(self):
        return reverse('catalogue:auteur-detail', kwargs={'slug': self.slug})
    
    def nombre_livres(self):
        return self.livres.count()
    nombre_livres.short_description = "Nombre de livres"

    def biographie_texte(self):
        from html import unescape
        return unescape(strip_tags(self.biographie or ""))

    def biographie_html(self):
        from html import unescape
        return unescape(self.biographie or "")


# -------------------------------------------------------------------------------
# MODÈLE LIVRE
# -------------------------------------------------------------------------------

class Livre(TimeStampedModel, SEOModel):
    """Modèle Livre."""
    
    LANGUES = [
        ("fr", "Français"),
        ("en", "Anglais"),
        ("de", "Allemand"),
        ("ja", "Japonais"),
        ("zh", "Mandarin"),
        ("ru", "Russe"),
        ("ar", "Arabe"),
        ("fon", "Fongbe"),
        ("yo", "Yoruba"),
        ("ha", "Haoussa"),
        ("sw", "Swahili"),
        ("es", "Espagnol"),
        ("pt", "Portugais"),
    ]
    
    CATEGORIES = [
        ('roman', 'Roman'),
        ('poemes', 'Poèmes'),
        ('essai', 'Essai'),
        ('policiers', 'Polars/Thrillers'),
        ('bd', 'BD'),
        ('theatres', 'Théâtres'),
        ('nouvelles', 'Nouvelles'),
        ('litterature-fr', 'Littérature française'),
        ('litterature-etr', 'Littérature étrangère'),
        ('beaux-livres', 'Beaux livres'),
        ('jeunesse', 'Jeunesse'),
        ('sh', 'Sciences humaines'),
    ]
    
    titre = models.CharField(max_length=300, verbose_name="Titre", db_index=True)
    auteurs = models.ManyToManyField(
        Auteur,
        related_name="livres",
        verbose_name="Auteurs",
        help_text="Sélectionnez un ou plusieurs auteurs.",
    )
    categorie = models.CharField(max_length=50, choices=CATEGORIES, verbose_name="Cat\u00e9gorie", db_index=True)
    collection = models.ForeignKey(
        "Collection",
        on_delete=models.SET_NULL,
        related_name="livres",
        blank=True,
        null=True,
        verbose_name="Collection",
    )
    resume = models.TextField(verbose_name="R\u00e9sum\u00e9")
    isbn = models.CharField(max_length=20, unique=True, verbose_name="ISBN", db_index=True)
    prix = models.CharField(max_length=50, verbose_name="Prix")
    parution = models.DateField(verbose_name="Date de parution", db_index=True)
    langue_publication = models.CharField(
        max_length=10,
        choices=LANGUES,
        default="fr",
        verbose_name="Langue de publication",
        db_index=True,
    )
    version_papier = models.BooleanField(default=True, verbose_name="Version papier disponible", db_index=True)
    version_numerique = models.BooleanField(default=False, verbose_name="Version numérique disponible", db_index=True)
    version_audio = models.BooleanField(default=False, verbose_name="Version audio disponible", db_index=True)
    
    image = models.ImageField(upload_to='books/%Y/%m/', verbose_name="Couverture version papier")
    image_numerique = models.ImageField(
        upload_to='books/numerique/%Y/%m/',
        verbose_name="Couverture version numérique",
        blank=True,
        null=True,
    )
    image_audio = models.ImageField(
        upload_to='books/audio/%Y/%m/',
        verbose_name="Couverture version audio",
        blank=True,
        null=True,
    )
    
    lien_chariow = models.URLField(max_length=500, verbose_name="Lien Recréation shop (papier)", blank=True, null=True)
    lien_amazon = models.URLField(max_length=500, verbose_name="Lien Amazon (papier)", blank=True, null=True)
    lien_whatsapp = models.URLField(max_length=500, verbose_name="Lien WhatsApp (papier)", blank=True, null=True)
    lien_chariow_numerique = models.URLField(
        max_length=500,
        verbose_name="Lien Recréation shop (numérique)",
        blank=True,
        null=True,
    )
    lien_amazon_numerique = models.URLField(
        max_length=500,
        verbose_name="Lien Amazon (numérique)",
        blank=True,
        null=True,
    )
    lien_whatsapp_numerique = models.URLField(
        max_length=500,
        verbose_name="Lien WhatsApp (numérique)",
        blank=True,
        null=True,
    )
    lien_chariow_audio = models.URLField(
        max_length=500,
        verbose_name="Lien Recréation shop (audio)",
        blank=True,
        null=True,
    )
    lien_amazon_audio = models.URLField(
        max_length=500,
        verbose_name="Lien Amazon (audio)",
        blank=True,
        null=True,
    )
    lien_whatsapp_audio = models.URLField(
        max_length=500,
        verbose_name="Lien WhatsApp (audio)",
        blank=True,
        null=True,
    )
    
    slug = models.SlugField(max_length=350, unique=True, blank=True, verbose_name="Slug")
    
    est_nouveau = models.BooleanField(default=False, verbose_name="Est nouveau", db_index=True)
    est_bestseller = models.BooleanField(default=False, verbose_name="Est bestseller", db_index=True)
    est_prochaine_parution = models.BooleanField(default=False, verbose_name="Est prochaine parution", db_index=True)
    est_publie = models.BooleanField(default=True, verbose_name="Est publié", db_index=True)
    
    objects = LivreManager()
    
    class Meta:
        verbose_name = "Livre"
        verbose_name_plural = "Livres"
        ordering = ['-parution', '-created_at']
        indexes = [
            models.Index(fields=['titre']),
            models.Index(fields=['-parution', 'categorie']),
            models.Index(fields=['est_publie']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titre)
            slug = base_slug
            counter = 1
            while Livre.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        auteur = self.auteurs.first()
        return f"{self.titre} - {auteur.nom}" if auteur else self.titre

    def auteurs_noms(self):
        noms = [a.nom for a in self.auteurs.all()]
        if not noms:
            return ""
        if len(noms) == 1:
            return noms[0]
        if len(noms) == 2:
            return f"{noms[0]} et {noms[1]}"
        return f"{', '.join(noms[:-1])} et {noms[-1]}"
    
    def get_absolute_url(self):
        return reverse('catalogue:livre-detail', kwargs={'slug': self.slug})

    def image_par_defaut(self):
        return self.image or self.image_numerique or self.image_audio
    
    def image_pour_version(self, version):
        version = (version or "").lower().strip()
        if version == "numerique":
            return self.image_numerique or self.image or self.image_audio
        if version == "audio":
            return self.image_audio or self.image or self.image_numerique
        if version == "papier":
            return self.image or self.image_numerique or self.image_audio
        return self.image_par_defaut()
    
    def versions_disponibles(self):
        versions = []
        if self.version_papier:
            versions.append("papier")
        if self.version_numerique:
            versions.append("numerique")
        if self.version_audio:
            versions.append("audio")
        return versions


# -------------------------------------------------------------------------------
# MODÈLE MEMBRE
# -------------------------------------------------------------------------------

class Membre(TimeStampedModel):
    """Modèle Membre de l'équipe."""
    
    nom_complet = models.CharField(max_length=200, verbose_name="Nom complet")
    poste = models.CharField(max_length=150, verbose_name="Poste/Rôle")
    photo = models.ImageField(upload_to='team/%Y/%m/', verbose_name="Photo")
    biographie = RichTextField(blank=True, verbose_name="Biographie courte")
    email = models.EmailField(blank=True, verbose_name="Email professionnel")
    ordre_affichage = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    nationalites = models.ManyToManyField(
        Nationalite,
        blank=True,
        related_name="membres",
        verbose_name="Nationalités",
        help_text="Sélectionnez une ou plusieurs nationalités.",
    )
    
    class Meta:
        verbose_name = "Membre de l'équipe"
        verbose_name_plural = "Membres de l'équipe"
        ordering = ['ordre_affichage', 'nom_complet']
    
    def __str__(self):
        return f"{self.nom_complet} - {self.poste}"


# -------------------------------------------------------------------------------
# MODÈLE PRIX LITTERAIRE
# -------------------------------------------------------------------------------

class PrixLitteraire(TimeStampedModel):
    """Modèle Prix littéraire."""
    
    titre = models.CharField(max_length=200, verbose_name="Nom du prix")
    annee = models.PositiveIntegerField(blank=True, null=True, verbose_name="Année")
    auteur = models.ForeignKey(
        Auteur,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="prix_litteraires",
        verbose_name="Auteur",
    )
    livre = models.ForeignKey(
        Livre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="prix_litteraires",
        verbose_name="Livre",
    )
    description = models.TextField(blank=True, verbose_name="Description")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Prix littéraire"
        verbose_name_plural = "Prix littéraires"
        ordering = ["-annee", "titre"]
    
    def __str__(self):
        return f"{self.titre} ({self.annee})" if self.annee else self.titre


# -------------------------------------------------------------------------------
# MODÈLE ACTUALITÉ
# -------------------------------------------------------------------------------

class Actualite(TimeStampedModel, SEOModel):
    """Modèle Actualité."""
    
    titre = models.CharField(max_length=250, verbose_name="Titre")
    slug = models.SlugField(max_length=300, unique=True, blank=True, verbose_name="Slug")
    image = models.ImageField(upload_to='news/%Y/%m/', verbose_name="Image")
    extrait = RichTextField(max_length=300, verbose_name="Extrait")
    contenu = RichTextField(verbose_name="Contenu")
    date_publication = models.DateField(verbose_name="Date de publication")
    est_publie = models.BooleanField(default=True, verbose_name="Est publié")
    est_une_a_la_une = models.BooleanField(default=False, verbose_name="À la une")
    
    class Meta:
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"
        ordering = ['-date_publication', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titre)
            slug = base_slug
            counter = 1
            while Actualite.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.titre
    
    def get_absolute_url(self):
        return reverse('catalogue:actualite-detail', kwargs={'slug': self.slug})


# -------------------------------------------------------------------------------
# MODÈLE INSCRIPTION NEWSLETTER
# -------------------------------------------------------------------------------

class InscriptionNewsletter(TimeStampedModel):
    """Modèle Inscription Newsletter."""
    
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    est_actif = models.BooleanField(default=True, verbose_name="Inscription active")
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    
    class Meta:
        verbose_name = "Inscription Newsletter"
        verbose_name_plural = "Inscriptions Newsletter"
        ordering = ['-date_inscription']
    
    def __str__(self):
        return self.email


# -------------------------------------------------------------------------------
# MODÈLE CONVERSION TEXTE EN AUDIO
# -------------------------------------------------------------------------------

class AudioConversionRequest(TimeStampedModel):
    """Demande de conversion texte en audio."""
    
    STATUS_CHOICES = [
        ("free_generated", "Audio généré (gratuit)"),
        ("awaiting_payment", "En attente de paiement"),
        ("paid", "Payé"),
        ("processing", "En traitement"),
        ("delivered", "Envoyé"),
        ("error", "Erreur"),
    ]

    ASYNC_STATUS_CHOICES = [
        ("queued", "En file d'attente"),
        ("started", "En cours"),
        ("finished", "Terminé"),
        ("failed", "Échec"),
    ]
    
    VOICE_CHOICES = [
        ("slow", "Lent"),
        ("standard", "Normal"),
        ("fast", "Rapide"),
    ]
    
    LANG_CHOICES = [
        ("fr", "Français"),
        ("en", "Anglais"),
        ("es", "Espagnol"),
        ("de", "Allemand"),
        ("fon", "Fon"),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="audio_conversions",
        verbose_name="Utilisateur",
    )
    email = models.EmailField(verbose_name="Email", blank=True)
    whatsapp = models.CharField(max_length=40, verbose_name="WhatsApp", blank=True)
    texte = models.TextField(blank=True, verbose_name="Texte")
    fichier = models.FileField(upload_to="audio_requests/files/%Y/%m/", blank=True, null=True, verbose_name="Fichier")
    phrases_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de phrases")
    langue = models.CharField(max_length=10, choices=LANG_CHOICES, default="fr", verbose_name="Langue")
    voix = models.CharField(max_length=20, choices=VOICE_CHOICES, default="standard", verbose_name="Voix")
    audio = models.FileField(upload_to="audio_requests/audio/%Y/%m/", blank=True, null=True, verbose_name="Audio généré")
    paiement_requis = models.BooleanField(default=False, verbose_name="Paiement requis")
    statut = models.CharField(max_length=30, choices=STATUS_CHOICES, default="awaiting_payment", verbose_name="Statut")
    paiement_initie_at = models.DateTimeField(blank=True, null=True, verbose_name="Paiement initié le")
    pages_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de pages (estimé)")
    payment_tier = models.PositiveSmallIntegerField(default=1, verbose_name="Palier de paiement")
    lecture_humaine = models.BooleanField(default=False, verbose_name="Lecture par un humain")
    voix_humaine = models.CharField(
        max_length=10,
        blank=True,
        default="",
        choices=[
            ("male", "Voix masculine"),
            ("female", "Voix féminine"),
        ],
        verbose_name="Voix (lecture par un humain)",
    )
    async_status = models.CharField(
        max_length=20,
        choices=ASYNC_STATUS_CHOICES,
        blank=True,
        default="",
        verbose_name="Statut de conversion",
    )
    async_progress = models.PositiveIntegerField(default=0, verbose_name="Progression (%)")
    async_error = models.TextField(blank=True, verbose_name="Erreur conversion")
    async_started_at = models.DateTimeField(blank=True, null=True, verbose_name="Début conversion")
    async_finished_at = models.DateTimeField(blank=True, null=True, verbose_name="Fin conversion")
    
    class Meta:
        verbose_name = "Conversion texte en audio"
        verbose_name_plural = "Conversions texte en audio"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.email} - {self.statut}"


class AudioConversionGenerated(AudioConversionRequest):
    """Proxy pour afficher uniquement les audios générés."""

    class Meta:
        proxy = True
        verbose_name = "Audio généré"
        verbose_name_plural = "Audios générés"


class AudioConversionChunk(TimeStampedModel):
    """Segment audio généré pour une demande de conversion."""

    request = models.ForeignKey(
        AudioConversionRequest,
        on_delete=models.CASCADE,
        related_name="chunks",
        verbose_name="Demande",
    )
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")
    start_page = models.PositiveIntegerField(default=1, verbose_name="Page de début")
    end_page = models.PositiveIntegerField(default=1, verbose_name="Page de fin")
    audio = models.FileField(
        upload_to="audio_requests/chunks/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Audio (segment)",
    )
    error = models.TextField(blank=True, verbose_name="Erreur")

    class Meta:
        ordering = ["order"]
        verbose_name = "Segment audio"
        verbose_name_plural = "Segments audio"

    def __str__(self):
        return f"{self.request_id} - Partie {self.order}"


class UserProfile(TimeStampedModel):
    """Profil utilisateur (infos complémentaires)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Utilisateur",
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    newsletter_opt_in = models.BooleanField(default=False, verbose_name="Inscrit à la newsletter")

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"{self.user.get_username()}"


# -------------------------------------------------------------------------------
# MODÈLE MESSAGE CONTACT
# -------------------------------------------------------------------------------

class MessageContact(TimeStampedModel):
    """Modèle Message Contact."""
    
    STATUT_CHOICES = [
        ('nouveau', 'Nouveau'),
        ('en_cours', 'En cours'),
        ('traite', 'Traité'),
        ('archive', 'Archivé'),
    ]
    
    nom = models.CharField(max_length=200, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Email")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    sujet = models.CharField(max_length=250, verbose_name="Sujet")
    message = RichTextField(verbose_name="Message")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='nouveau', verbose_name="Statut")
    date_reception = models.DateTimeField(auto_now_add=True, verbose_name="Date réception")
    lu = models.BooleanField(default=False, verbose_name="Lu")
    notes_admin = RichTextField(blank=True, verbose_name="Notes admin")
    
    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-date_reception']
    
    def __str__(self):
        return f"{self.nom} - {self.sujet}"


# -------------------------------------------------------------------------------
# MODÈLE SOUMISSION MANUSCRIT
# -------------------------------------------------------------------------------

class SoumissionManuscrit(TimeStampedModel):
    """Modèle Soumission de manuscrit."""

    CONTRACT_CHOICES = [
        ("compte_editeur", "Contrat à compte d'éditeur"),
        ("compte_auteur", "Contrat à compte d'auteur"),
        ("compte_participatif", "Contrat à compte participatif"),
    ]

    nom_complet = models.CharField(max_length=200, verbose_name="Nom et prénom à l'état civil")
    nom_auteur = models.CharField(max_length=200, verbose_name="Nom ou pseudonyme d'auteur")
    whatsapp = models.CharField(max_length=40, verbose_name="Numéro de téléphone WhatsApp", default="")
    autre_numero = models.CharField(max_length=40, blank=True, verbose_name="Autre numéro de l'auteur")
    nationalite = models.CharField(max_length=120, verbose_name="Nationalité", default="")
    pays_residence = models.CharField(max_length=120, verbose_name="Pays de résidence", default="")
    titre_ouvrage = models.CharField(max_length=300, verbose_name="Titre de l'ouvrage")
    genre_litteraire = models.CharField(max_length=150, verbose_name="Genre littéraire")
    type_contrat = models.CharField(
        max_length=40,
        choices=CONTRACT_CHOICES,
        verbose_name="Type de contrat souhaité",
        default="compte_auteur",
    )
    synopsis = models.TextField(verbose_name="Synopsis ou résumé")
    avantages = RichTextField(verbose_name="Avantages pour les lecteurs")
    inconvenients = models.TextField(verbose_name="Inconvénients pour les lecteurs")

    fichier_ouvrage = models.FileField(upload_to='soumissions/manuscrits/%Y/%m/', verbose_name="Fichier de l'ouvrage")
    photo_auteur = models.ImageField(upload_to='soumissions/auteurs/%Y/%m/', verbose_name="Photo de l'auteur")
    carte_identite = models.FileField(upload_to='soumissions/cartes/%Y/%m/', verbose_name="Carte d'identité")

    class Meta:
        verbose_name = "Soumission de manuscrit"
        verbose_name_plural = "Soumissions de manuscrits"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titre_ouvrage} - {self.nom_auteur}"


# -------------------------------------------------------------------------------
# MODÈLE PUBLICITÉ SITE
# -------------------------------------------------------------------------------

class SiteAd(TimeStampedModel):
    """Bannière publicitaire diffusée sur le site."""

    title = models.CharField(max_length=200, blank=True, verbose_name="Titre")
    text = models.CharField(max_length=255, blank=True, verbose_name="Texte court")
    image = models.ImageField(upload_to="ads/%Y/%m/", verbose_name="Image")
    link_url = models.URLField(blank=True, verbose_name="Lien de redirection")
    weight = models.PositiveSmallIntegerField(default=1, verbose_name="Poids de diffusion")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    starts_at = models.DateTimeField(blank=True, null=True, verbose_name="Début de diffusion")
    ends_at = models.DateTimeField(blank=True, null=True, verbose_name="Fin de diffusion")

    class Meta:
        verbose_name = "Publicité"
        verbose_name_plural = "Publicités"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"Publicité #{self.pk}"
