"""
FICHIER : apps/catalogue/admin.py
"""

from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django import forms
from django.utils.html import format_html
from ckeditor.fields import RichTextField
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from unfold.admin import ModelAdmin

from .utils.audio_conversion import extract_text_from_file, generate_tts_mp3
from .models import (
    Actualite,
    Auteur,
    Collection,
    InscriptionNewsletter,
    Livre,
    MenuLink,
    Membre,
    MessageContact,
    Nationalite,
    AudioConversionRequest,
    Page,
    PageBlock,
    PageBlockItem,
    PrixLitteraire,
    SoumissionManuscrit,
    UserProfile,
)
from apps.core.models import SiteAppearance


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = (UserProfileInline,)


@admin.register(Auteur)
class AuteurAdmin(ModelAdmin):
    formfield_overrides = {
        RichTextField: {"widget": CKEditorUploadingWidget},
    }
    list_display = ("nom", "specialite", "nationalites_affichage", "nombre_livres", "created_at")
    list_filter = ("specialite", "nationalites", "created_at")
    search_fields = ("nom", "biographie", "specialite")
    prepopulated_fields = {"slug": ("nom",)}
    readonly_fields = ("created_at", "updated_at", "nombre_livres")
    filter_horizontal = ("nationalites",)

    fieldsets = (
        ("Informations principales", {"fields": ("nom", "specialite", "photo", "nationalites")}),
        ("Biographie", {"fields": ("biographie",)}),
        ("SEO", {"fields": ("slug", "meta_title", "meta_description"), "classes": ("collapse",)}),
        ("Statistiques", {"fields": ("nombre_livres", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def apercu_photo(self, obj):
        """Afficher un apercu de la photo."""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 8px;">',
                obj.photo.url,
            )
        return "Aucune photo"

    apercu_photo.short_description = "Aper\u00e7u de la photo"

    def nationalites_affichage(self, obj):
        return ", ".join(nat.nom for nat in obj.nationalites.all())

    nationalites_affichage.short_description = "Nationalit\u00e9s"


@admin.register(Livre)
class LivreAdmin(ModelAdmin):
    formfield_overrides = {
        RichTextField: {"widget": CKEditorUploadingWidget},
        models.TextField: {"widget": CKEditorUploadingWidget},
    }
    list_display = (
        "titre",
        "auteurs_affichage",
        "categorie",
        "langue_publication",
        "prix",
        "parution",
        "est_nouveau",
        "est_bestseller",
        "est_prochaine_parution",
        "est_publie",
    )
    list_editable = ("est_nouveau", "est_bestseller", "est_prochaine_parution", "est_publie")
    list_filter = (
        "categorie",
        "collection",
        "langue_publication",
        "version_papier",
        "version_numerique",
        "version_audio",
        "est_nouveau",
        "est_bestseller",
        "est_prochaine_parution",
        "est_publie",
        "parution",
        "auteurs",
    )
    search_fields = ("titre", "auteurs__nom", "isbn", "collection__nom", "resume")
    prepopulated_fields = {"slug": ("titre",)}
    date_hierarchy = "parution"
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 30
    filter_horizontal = ("auteurs",)
    list_select_related = ("collection",)

    fieldsets = (
        ("Informations principales", {"fields": ("titre", "auteurs", "categorie", "collection", "langue_publication")}),
        ("Contenu", {"fields": ("resume",)}),
        ("D\u00e9tails publication", {"fields": ("isbn", "prix", "parution")}),
        ("Versions disponibles", {"fields": ("version_papier", "version_numerique", "version_audio")}),
        ("Couvertures par version", {"fields": ("image", "image_numerique", "image_audio")}),
        ("Liens d'achat (papier)", {"fields": ("lien_chariow", "lien_amazon", "lien_whatsapp")}),
        ("Liens d'achat (num\u00e9rique)", {"fields": ("lien_chariow_numerique", "lien_amazon_numerique", "lien_whatsapp_numerique")}),
        ("Liens d'achat (audio)", {"fields": ("lien_chariow_audio", "lien_amazon_audio", "lien_whatsapp_audio")}),
        ("Mise en avant", {"fields": ("est_nouveau", "est_bestseller", "est_prochaine_parution", "est_publie")}),
        ("SEO", {"fields": ("slug", "meta_title", "meta_description"), "classes": ("collapse",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["marquer_nouveau", "marquer_bestseller", "marquer_prochaine_parution", "publier", "depublier"]

    def auteurs_affichage(self, obj):
        return ", ".join(a.nom for a in obj.auteurs.all())

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("auteurs")

    auteurs_affichage.short_description = "Auteurs"

    def marquer_nouveau(self, request, queryset):
        updated = queryset.update(est_nouveau=True)
        self.message_user(request, f"{updated} livre(s) marqu\u00e9(s) comme nouveau")

    marquer_nouveau.short_description = "Marquer comme nouveau"

    def marquer_bestseller(self, request, queryset):
        updated = queryset.update(est_bestseller=True)
        self.message_user(request, f"{updated} livre(s) marqu\u00e9(s) comme bestseller")

    marquer_bestseller.short_description = "Marquer comme bestseller"

    def marquer_prochaine_parution(self, request, queryset):
        updated = queryset.update(est_prochaine_parution=True)
        self.message_user(request, f"{updated} livre(s) marqu\u00e9(s) comme prochaine parution")

    marquer_prochaine_parution.short_description = "Marquer comme prochaine parution"

    def publier(self, request, queryset):
        updated = queryset.update(est_publie=True)
        self.message_user(request, f"{updated} livre(s) publi\u00e9(s)")

    publier.short_description = "Publier"

    def depublier(self, request, queryset):
        updated = queryset.update(est_publie=False)
        self.message_user(request, f"{updated} livre(s) d\u00e9publi\u00e9(s)")

    depublier.short_description = "D\u00e9publier"

    def apercu_couverture(self, obj):
        """Grande previsualisation de la couverture."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 400px; max-width: 300px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">',
                obj.image.url,
            )
        return "Aucune image"

    apercu_couverture.short_description = "Aper\u00e7u de la couverture"

    def apercu_couverture_mini(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 60px; width: auto; border-radius: 4px;">', obj.image.url)
        return "\u274c"

    apercu_couverture_mini.short_description = "\U0001f4f7"

    def badge_nouveau(self, obj):
        if obj.est_nouveau:
            return format_html('<span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem;">\u2728 Nouveau</span>')
        return ""

    badge_nouveau.short_description = "Nouveau"

    def badge_bestseller(self, obj):
        if obj.est_bestseller:
            return format_html('<span style="background: #f59e0b; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem;">\U0001f525 Best</span>')
        return ""

    badge_bestseller.short_description = "Best"

    def badge_prochaine_parution(self, obj):
        if obj.est_prochaine_parution:
            return format_html('<span style="background: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem;">\U0001f4c5 Bient\u00f4t</span>')
        return ""

    badge_prochaine_parution.short_description = "Bient\u00f4t"


@admin.register(Membre)
class MembreAdmin(ModelAdmin):
    formfield_overrides = {
        RichTextField: {"widget": CKEditorUploadingWidget},
    }
    list_display = ("nom_complet", "poste", "nationalites_affichage", "ordre_affichage", "est_actif", "created_at")
    list_editable = ("ordre_affichage", "est_actif")
    list_filter = ("est_actif", "created_at")
    search_fields = ("nom_complet", "poste", "biographie", "nationalites__nom", "nationalites__code_iso")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("nationalites",)

    fieldsets = (
        ("Informations", {"fields": ("nom_complet", "poste", "photo", "nationalites")}),
        ("Biographie", {"fields": ("biographie", "email")}),
        ("Affichage", {"fields": ("ordre_affichage", "est_actif")}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def apercu_photo(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px; border-radius: 50%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">',
                obj.photo.url,
            )
        return "Aucune photo"

    apercu_photo.short_description = "Aper\u00e7u"

    def apercu_photo_mini(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height: 40px; width: 40px; border-radius: 50%; object-fit: cover;">', obj.photo.url)
        return "\U0001f464"

    apercu_photo_mini.short_description = "\U0001f4f7"
    
    def nationalites_affichage(self, obj):
        return ", ".join(nat.nom for nat in obj.nationalites.all())
    
    nationalites_affichage.short_description = "Nationalités"


@admin.register(Nationalite)
class NationaliteAdmin(ModelAdmin):
    list_display = ("nom", "code_iso", "apercu_drapeau")
    search_fields = ("nom", "code_iso")
    ordering = ("nom",)

    def apercu_drapeau(self, obj):
        if obj.drapeau:
            return format_html(
                '<img src="{}" style="height: 28px; width: auto; border-radius: 6px;">',
                obj.drapeau.url,
            )
        return "\u274c"

    apercu_drapeau.short_description = "Drapeau"


@admin.register(Page)
class PageAdmin(ModelAdmin):
    formfield_overrides = {
        RichTextField: {"widget": CKEditorUploadingWidget},
    }
    list_display = ("title", "slug", "is_active", "show_team", "created_at")
    list_display_links = ("title",)
    list_editable = ("is_active", "show_team")
    search_fields = ("title", "slug", "body")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    view_on_site = False
    
    class PageBlockInline(admin.TabularInline):
        model = PageBlock
        extra = 0
        fields = ("block_type", "ordre", "titre", "apercu_inline", "est_actif")
        ordering = ("ordre",)
        show_change_link = True
        readonly_fields = ("apercu_inline",)
        
        def apercu_inline(self, obj):
            if not obj:
                return ""
            if obj.image:
                return format_html(
                    '<img src="{}" style="height:36px;width:36px;object-fit:cover;border-radius:6px;">',
                    obj.image.url,
                )
            return format_html(
                '<span style="color:#6b7280;">{}</span>',
                obj.titre or obj.get_block_type_display(),
            )
        
        apercu_inline.short_description = "Aperçu"
    
    inlines = [PageBlockInline]
    
    class Media:
        css = {"all": ("catalogue/admin/inline_sortable.css",)}
        js = ("catalogue/admin/inline_sortable.js",)

    fieldsets = (
        ("Contenu", {"fields": ("title", "slug", "hero_title", "hero_subtitle", "body")}),
        ("Options", {"fields": ("is_active", "show_team")}),
        ("SEO", {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Collection)
class CollectionAdmin(ModelAdmin):
    formfield_overrides = {
        RichTextField: {"widget": CKEditorUploadingWidget},
    }
    list_display = ("nom", "est_active", "ordre_affichage", "created_at")
    list_editable = ("est_active", "ordre_affichage")
    search_fields = ("nom", "description")
    prepopulated_fields = {"slug": ("nom",)}
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Informations", {"fields": ("nom", "slug", "image")}),
        ("Description", {"fields": ("description",)}),
        ("Affichage", {"fields": ("ordre_affichage", "est_active")}),
        ("SEO", {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(MenuLink)
class MenuLinkAdmin(ModelAdmin):
    list_display = ("title", "url", "location", "order", "is_active")
    list_editable = ("location", "order", "is_active")
    list_filter = ("location", "is_active")
    search_fields = ("title", "url")
    ordering = ("location", "order", "title")
    actions = ["reinitialiser_menu"]
    
    class MenuLinkActionForm(forms.Form):
        confirmer_reinitialisation = forms.BooleanField(
            required=False,
            label="Confirmer la réinitialisation du menu",
        )

    action_form = MenuLinkActionForm

    def reinitialiser_menu(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(request, "Action réservée aux super-admins.", level="error")
            return
        if not request.POST.get("confirmer_reinitialisation"):
            self.message_user(request, "Veuillez cocher la confirmation avant de réinitialiser.", level="warning")
            return
        MenuLink.objects.filter(location__in=["header", "footer"]).delete()

        header_links = [
            ("Accueil", "/", 1),
            ("Actualités", "/actualites/", 2),
            ("Auteurs", "/auteurs/", 3),
            ("Catalogue", "/catalogue/", 4),
            ("Nos contrats", "/nos-contrats/", 5),
            ("A propos", "/a-propos/", 6),
            ("Contacts", "/contact/", 7),
        ]
        for title, url, order in header_links:
            MenuLink.objects.create(
                title=title,
                url=url,
                location="header",
                order=order,
                is_active=True,
            )

        footer_links = [
            ("Mentions legales", "/mentions-legales/", 1),
            ("Confidentialite", "/confidentialite/", 2),
            ("Cookies", "/cookies/", 3),
        ]
        for title, url, order in footer_links:
            MenuLink.objects.create(
                title=title,
                url=url,
                location="footer",
                order=order,
                is_active=True,
            )

        self.message_user(request, "Menu reinitialise avec les valeurs par defaut.")

    reinitialiser_menu.short_description = "Reinitialiser le menu (valeurs par defaut)"


@admin.register(Actualite)
class ActualiteAdmin(ModelAdmin):
    class ActualiteAdminForm(forms.ModelForm):
        class Meta:
            model = Actualite
            fields = "__all__"
            widgets = {
                "extrait": CKEditorUploadingWidget(),
                "contenu": CKEditorUploadingWidget(),
            }

    form = ActualiteAdminForm
    formfield_overrides = {
        RichTextField: {"widget": CKEditorUploadingWidget},
    }
    list_display = ("titre", "date_publication", "est_publie", "est_une_a_la_une", "created_at")
    list_editable = ("est_publie", "est_une_a_la_une")
    list_filter = ("est_publie", "est_une_a_la_une", "date_publication")
    search_fields = ("titre", "extrait", "contenu")
    prepopulated_fields = {"slug": ("titre",)}
    date_hierarchy = "date_publication"
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Informations principales", {"fields": ("titre", "image", "date_publication")}),
        ("Contenu", {"fields": ("extrait", "contenu")}),
        ("Mise en avant", {"fields": ("est_publie", "est_une_a_la_une")}),
        ("SEO", {"fields": ("slug", "meta_title", "meta_description"), "classes": ("collapse",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["publier", "depublier"]

    def publier(self, request, queryset):
        updated = queryset.update(est_publie=True)
        self.message_user(request, f"{updated} actualit\u00e9(s) publi\u00e9e(s)")

    publier.short_description = "Publier"

    def depublier(self, request, queryset):
        updated = queryset.update(est_publie=False)
        self.message_user(request, f"{updated} actualit\u00e9(s) d\u00e9publi\u00e9e(s)")

    depublier.short_description = "D\u00e9publier"

    def apercu_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 300px; max-width: 100%; border-radius: 8px;">', obj.image.url)
        return "Aucune image"

    apercu_image.short_description = "Aper\u00e7u"

    def apercu_image_mini(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 50px; width: auto; border-radius: 4px;">', obj.image.url)
        return "\U0001f5bc\ufe0f"

    apercu_image_mini.short_description = "\U0001f4f7"

    def badge_publie(self, obj):
        if obj.est_publie:
            return format_html('<span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 4px;">\u2705 Publi\u00e9</span>')
        return format_html('<span style="background: #6b7280; color: white; padding: 4px 8px; border-radius: 4px;">\u274c Brouillon</span>')

    badge_publie.short_description = "Statut"

    def badge_une(self, obj):
        if obj.est_une_a_la_une:
            return format_html('<span style="background: #f59e0b; color: white; padding: 4px 8px; border-radius: 4px;">\u2b50 \u00c0 la une</span>')
        return ""

    badge_une.short_description = "Une"


@admin.register(PrixLitteraire)
class PrixLitteraireAdmin(ModelAdmin):
    list_display = ("titre", "annee", "auteur", "livre", "est_actif", "created_at")
    list_editable = ("est_actif",)
    list_filter = ("est_actif", "annee")
    search_fields = ("titre", "auteur__nom", "livre__titre")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("auteur", "livre")
    fieldsets = (
        ("Informations", {"fields": ("titre", "annee", "est_actif")}),
        ("Associations", {"fields": ("auteur", "livre")}),
        ("Description", {"fields": ("description",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(PageBlock)
class PageBlockAdmin(ModelAdmin):
    formfield_overrides = {
        RichTextField: {"widget": CKEditorUploadingWidget},
    }
    list_display = ("page", "block_type", "ordre", "titre", "apercu", "est_actif")
    list_editable = ("ordre", "est_actif")
    list_filter = ("block_type", "est_actif", "page")
    search_fields = ("page__title", "titre", "contenu")
    readonly_fields = ("created_at", "updated_at")
    
    class PageBlockItemInline(admin.TabularInline):
        model = PageBlockItem
        extra = 0
        fields = ("ordre", "titre", "sous_titre", "image", "icone", "lien_texte", "lien_url", "est_actif")
        ordering = ("ordre",)
    
    inlines = [PageBlockItemInline]
    
    class Media:
        css = {"all": ("catalogue/admin/inline_sortable.css",)}
        js = ("catalogue/admin/inline_sortable.js",)
    
    fieldsets = (
        ("Identification", {"fields": ("page", "block_type", "ordre", "est_actif")}),
        ("Texte", {"fields": ("titre", "sous_titre", "contenu")}),
        ("Visuel", {"fields": ("image",)}),
        ("Bouton", {"fields": ("bouton_texte", "bouton_url")}),
        ("Style", {"fields": ("css_class",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    
    def apercu(self, obj):
        if obj.image:
            return format_html(
                '<div style="display:flex;align-items:center;gap:8px;">'
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px;">'
                '<span>{}</span></div>',
                obj.image.url,
                obj.titre or obj.get_block_type_display(),
            )
        return format_html(
            '<span style="color:#6b7280;">{}</span>',
            obj.titre or obj.get_block_type_display(),
        )
    
    apercu.short_description = "Aperçu"


@admin.register(PageBlockItem)
class PageBlockItemAdmin(ModelAdmin):
    formfield_overrides = {
        RichTextField: {"widget": CKEditorUploadingWidget},
    }
    list_display = ("block", "ordre", "titre", "est_actif")
    list_editable = ("ordre", "est_actif")
    list_filter = ("block__block_type", "est_actif")
    search_fields = ("titre", "contenu")
    readonly_fields = ("created_at", "updated_at")


@admin.register(InscriptionNewsletter)
class InscriptionNewsletterAdmin(ModelAdmin):
    list_display = ("email", "est_actif", "date_inscription")
    list_editable = ("est_actif",)
    list_filter = ("est_actif", "date_inscription")
    search_fields = ("email",)
    readonly_fields = ("date_inscription", "created_at", "updated_at")
    date_hierarchy = "date_inscription"

    def badge_actif(self, obj):
        if obj.est_actif:
            return format_html('<span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 4px;">\u2705 Actif</span>')
        return format_html('<span style="background: #ef4444; color: white; padding: 4px 8px; border-radius: 4px;">\u274c Inactif</span>')


@admin.register(AudioConversionRequest)
class AudioConversionRequestAdmin(ModelAdmin):
    list_display = (
        "email",
        "whatsapp",
        "user",
        "pages_count",
        "payment_tier",
        "fichier_link",
        "audio_link",
        "lecture_humaine",
        "voix_humaine",
        "paiement_requis",
        "paiement_initie",
        "statut",
        "created_at",
    )
    list_filter = ("paiement_requis", "lecture_humaine", "paiement_initie_at", "statut", "langue", "voix", "created_at")
    search_fields = ("email", "whatsapp", "texte")
    list_editable = ("statut",)
    readonly_fields = ("created_at", "updated_at", "audio", "fichier", "paiement_initie_at", "pages_count", "payment_tier")
    date_hierarchy = "created_at"
    actions = ["convertir_fichier_en_audio", "marquer_paye"]
    change_list_template = "admin/catalogue/audioconversionrequest/change_list.html"
    list_select_related = ("user",)
    fieldsets = (
        ("Contact", {"fields": ("user", "email", "whatsapp")}),
        ("Demande", {"fields": ("texte", "fichier", "langue", "voix", "lecture_humaine", "voix_humaine")}),
        ("Statut", {"fields": ("pages_count", "payment_tier", "paiement_requis", "paiement_initie_at", "statut", "audio")}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def paiement_initie(self, obj):
        return bool(obj.paiement_initie_at)

    paiement_initie.boolean = True
    paiement_initie.short_description = "Paiement initié"

    def marquer_paye(self, request, queryset):
        from django.utils import timezone

        updated = 0
        for obj in queryset:
            if not obj.paiement_initie_at:
                obj.paiement_initie_at = timezone.now()
            obj.statut = "paid"
            obj.save(update_fields=["paiement_initie_at", "statut", "updated_at"])
            updated += 1
        if updated:
            self.message_user(request, f"{updated} demande(s) marquée(s) comme payée(s).", level="success")

    marquer_paye.short_description = "Marquer comme payée"

    def _generate_audio_for_obj(self, obj):
        from django.core.files.base import ContentFile
        from django.utils.text import slugify
        import uuid

        text = obj.texte or ""
        if obj.fichier and not text.strip():
            text = extract_text_from_file(obj.fichier)
        if not text.strip():
            raise RuntimeError("Texte vide après extraction.")
        audio_stream = generate_tts_mp3(text, lang="fr", slow=False, chunk_size=1000)
        audio_bytes = ContentFile(audio_stream.getvalue())
        filename = f"conversion-{slugify(obj.email) or obj.id}-{uuid.uuid4().hex}.mp3"
        obj.audio.save(filename, audio_bytes, save=False)
        obj.statut = "delivered"
        obj.save(update_fields=["audio", "statut", "updated_at"])

    def convertir_fichier_en_audio(self, request, queryset):
        from .tasks import convert_audio_request

        queued = 0
        for obj in queryset:
            if not obj.fichier and not obj.texte:
                self.message_user(request, f"Aucun texte/fichier pour la demande #{obj.id}.", level="warning")
                continue
            obj.statut = "processing"
            obj.async_status = "queued"
            obj.async_progress = 0
            obj.async_error = ""
            obj.save(update_fields=["statut", "async_status", "async_progress", "async_error", "updated_at"])
            convert_audio_request(obj.id)
            queued += 1
        if queued:
            self.message_user(request, f"{queued} demande(s) envoyée(s) en traitement.", level="success")

    convertir_fichier_en_audio.short_description = "Convertir le fichier en MP3"

    def fichier_link(self, obj):
        if obj.fichier:
            return format_html('<a href="{}" target="_blank">Télécharger</a>', obj.fichier.url)
        return "-"

    fichier_link.short_description = "Fichier"

    def audio_link(self, obj):
        if obj.audio:
            return format_html('<a href="{}" target="_blank">Télécharger MP3</a>', obj.audio.url)
        return "-"

    audio_link.short_description = "Audio"


@admin.register(MessageContact)
class MessageContactAdmin(ModelAdmin):
    formfield_overrides = {
        RichTextField: {"widget": CKEditorUploadingWidget},
        models.TextField: {"widget": CKEditorUploadingWidget},
    }
    list_display = ("nom", "email", "sujet", "statut", "lu", "date_reception")
    list_editable = ("statut", "lu")
    list_filter = ("statut", "lu", "date_reception")
    search_fields = ("nom", "email", "sujet", "message")
    readonly_fields = ("date_reception", "created_at", "updated_at")
    date_hierarchy = "date_reception"

    fieldsets = (
        ("Exp\u00e9diteur", {"fields": ("nom", "email", "telephone")}),
        ("Message", {"fields": ("sujet", "message")}),
        ("Gestion", {"fields": ("statut", "lu", "notes_admin")}),
        ("Dates", {"fields": ("date_reception", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["marquer_lu", "marquer_traite"]

    def marquer_lu(self, request, queryset):
        updated = queryset.update(lu=True)
        self.message_user(request, f"{updated} message(s) marqu\u00e9(s) comme lu")

    marquer_lu.short_description = "Marquer comme lu"

    def marquer_traite(self, request, queryset):
        updated = queryset.update(statut="traite", lu=True)
        self.message_user(request, f"{updated} message(s) trait\u00e9(s)")

    marquer_traite.short_description = "Marquer comme trait\u00e9"

    def badge_lu(self, obj):
        if obj.lu:
            return format_html('<span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 4px;">\u2705 Lu</span>')
        return format_html('<span style="background: #ef4444; color: white; padding: 4px 8px; border-radius: 4px;">\U0001f4e7 Non lu</span>')

    badge_lu.short_description = "Lu"


@admin.register(SoumissionManuscrit)
class SoumissionManuscritAdmin(ModelAdmin):
    formfield_overrides = {
        RichTextField: {"widget": CKEditorUploadingWidget},
        models.TextField: {"widget": CKEditorUploadingWidget},
    }
    list_display = ("titre_ouvrage", "nom_auteur", "nom_complet", "type_contrat", "nationalite", "pays_residence", "whatsapp", "created_at")
    list_filter = ("created_at",)
    search_fields = ("titre_ouvrage", "nom_auteur", "nom_complet", "whatsapp", "autre_numero", "nationalite", "pays_residence")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Identité", {"fields": ("nom_complet", "nom_auteur", "whatsapp", "autre_numero", "nationalite", "pays_residence")}),
        ("Ouvrage", {"fields": ("titre_ouvrage", "genre_litteraire", "type_contrat", "synopsis", "avantages", "inconvenients")}),
        ("Fichiers", {"fields": ("fichier_ouvrage", "photo_auteur", "carte_identite")}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
