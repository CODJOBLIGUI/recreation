"""
FICHIER : apps/catalogue/admin.py
"""

from django.contrib import admin
import os
from django.contrib.admin.helpers import ActionForm
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django import forms
from django.utils.dateparse import parse_date
from django.utils.html import format_html
from django.conf import settings
from django.urls import path
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.contrib import messages
from ckeditor.fields import RichTextField
from django_ckeditor_5.widgets import CKEditor5Widget
from unfold.admin import ModelAdmin

from .utils.audio_conversion import extract_text_from_file, normalize_tts_text, detect_tts_language
from apps.core.models import SiteAppearance
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
    AudioConversionGenerated,
    Page,
    PageBlock,
    PageBlockItem,
    PrixLitteraire,
    SoumissionManuscrit,
    UserProfile,
    ManuscriptReview,
    CommitteeApplication,
)
from apps.core.models import SiteAppearance


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


@admin.register(ManuscriptReview)
class ManuscriptReviewAdmin(ModelAdmin):
    list_display = ("soumission", "reviewer", "note", "decision", "created_at")
    list_filter = ("decision", "created_at")
    search_fields = ("soumission__titre_ouvrage", "reviewer__username", "reviewer__email")
    extra = 0


@admin.register(CommitteeApplication)
class CommitteeApplicationAdmin(ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    readonly_fields = ("created_at", "updated_at")


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
        RichTextField: {"widget": CKEditor5Widget(config_name="extends")},
    }
    list_display = ("nom", "specialite", "nationalites_affichage", "nombre_livres", "created_at")
    list_filter = ("specialite", "nationalites", "created_at")
    search_fields = ("nom", "biographie", "specialite")
    prepopulated_fields = {"slug": ("nom",)}
    readonly_fields = ("created_at", "updated_at", "nombre_livres")
    filter_horizontal = ("nationalites",)

    fieldsets = (
        ("Informations principales", {"fields": ("prefixe", "nom", "specialite", "photo", "nationalites")}),
        ("Biographie", {"fields": ("biographie",)}),
        ("SEO", {"fields": ("slug", "meta_title", "meta_description", "meta_keywords"), "classes": ("collapse",)}),
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
        RichTextField: {"widget": CKEditor5Widget(config_name="extends")},
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
        ("SEO", {"fields": ("slug", "meta_title", "meta_description", "meta_keywords"), "classes": ("collapse",)}),
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
        RichTextField: {"widget": CKEditor5Widget(config_name="extends")},
    }
    list_display = ("nom_complet", "poste", "nationalites_affichage", "ordre_affichage", "est_actif", "created_at")
    list_editable = ("ordre_affichage", "est_actif")
    list_filter = ("est_actif", "created_at")
    search_fields = ("nom_complet", "poste", "biographie", "biographie_longue", "nationalites__nom", "nationalites__code_iso")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("nationalites",)

    fieldsets = (
        ("Informations", {"fields": ("prefixe", "nom_complet", "poste", "photo", "nationalites")}),
        ("Biographie", {"fields": ("biographie", "biographie_longue")}),
        ("Contact", {"fields": ("email", "telephone", "site_web")}),
        ("Réseaux sociaux", {"fields": ("linkedin", "facebook", "x_twitter", "instagram", "tiktok", "youtube", "whatsapp")}),
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
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "biographie":
            kwargs["widget"] = CKEditor5Widget(config_name="simple")
        elif db_field.name == "biographie_longue":
            kwargs["widget"] = CKEditor5Widget(config_name="extends")
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
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
        RichTextField: {"widget": CKEditor5Widget(config_name="extends")},
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
        ("SEO", {"fields": ("meta_title", "meta_description", "meta_keywords"), "classes": ("collapse",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Collection)
class CollectionAdmin(ModelAdmin):
    formfield_overrides = {
        RichTextField: {"widget": CKEditor5Widget(config_name="extends")},
    }
    list_display = ("nom", "est_active", "ordre_affichage", "created_at")
    list_editable = ("est_active", "ordre_affichage")
    search_fields = ("nom", "description")
    prepopulated_fields = {"slug": ("nom",)}
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Informations", {"fields": ("nom", "slug", "logo", "image")}),
        ("Description", {"fields": ("description",)}),
        ("Affichage", {"fields": ("ordre_affichage", "est_active")}),
        ("SEO", {"fields": ("meta_title", "meta_description", "meta_keywords"), "classes": ("collapse",)}),
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
    
    class MenuLinkActionForm(ActionForm):
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
            ("Conversion de texte en audio", "/conversion-texte-audio/", 5),
            ("Nos contrats", "/nos-contrats/", 6),
            ("A propos", "/a-propos/", 7),
            ("Contacts", "/contact/", 8),
            ("Comité de lecture", "/lecture-evaluation-des-soumissions-de-manuscrit-ou-tapuscrits/", 9),
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
                "extrait": CKEditor5Widget(config_name="simple"),
                "contenu": CKEditor5Widget(config_name="extends"),
            }

    form = ActualiteAdminForm
    formfield_overrides = {
        RichTextField: {"widget": CKEditor5Widget(config_name="extends")},
    }
    list_display = ("titre", "date_publication", "est_publie", "est_une_a_la_une", "created_at")
    list_editable = ("est_publie", "est_une_a_la_une")
    list_filter = ("est_publie", "est_une_a_la_une", ("date_publication", admin.DateFieldListFilter))
    search_fields = ("titre", "extrait", "contenu")
    prepopulated_fields = {"slug": ("titre",)}
    date_hierarchy = "date_publication"
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Informations principales", {"fields": ("titre", "image", "date_publication")}),
        ("Contenu", {"fields": ("extrait", "contenu")}),
        ("Mise en avant", {"fields": ("est_publie", "est_une_a_la_une")}),
        ("SEO", {"fields": ("slug", "meta_title", "meta_description", "meta_keywords"), "classes": ("collapse",)}),
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
        RichTextField: {"widget": CKEditor5Widget(config_name="extends")},
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
        RichTextField: {"widget": CKEditor5Widget(config_name="extends")},
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
        "paiement_requis",
        "paiement_initie",
        "statut",
        "created_at",
    )
    list_filter = ("paiement_requis", "paiement_initie_at", "statut", "langue", "voix", "created_at")
    search_fields = ("email", "whatsapp", "texte")
    readonly_fields = (
        "created_at",
        "updated_at",
        "audio",
        "fichier",
        "paiement_initie_at",
        "pages_count",
        "payment_tier",
        "texte_normalise",
    )
    date_hierarchy = "created_at"
    actions = ["convertir_fichier_en_audio", "marquer_paye_et_envoyer"]
    change_list_template = "admin/catalogue/audioconversionrequest/change_list.html"
    change_form_template = "admin/catalogue/audioconversionrequest/change_form.html"
    list_select_related = ("user",)
    fieldsets = (
        ("Contact", {"fields": ("user", "email", "whatsapp")}),
        ("Demande", {"fields": ("texte", "texte_normalise", "use_original_text", "force_ocr", "fichier", "langue", "voix")}),
        ("Statut", {"fields": ("pages_count", "payment_tier", "paiement_requis", "paiement_initie_at", "statut", "audio")}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def save_model(self, request, obj, form, change):
        """Si statut passe à payé, générer l'audio (si absent)."""
        super().save_model(request, obj, form, change)
        if obj.statut == "paid" and not obj.audio:
            try:
                self._generate_audio_for_obj(obj)
            except Exception as exc:
                obj.statut = "error"
                obj.async_error = str(exc)
                obj.save(update_fields=["statut", "async_error", "updated_at"])

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:object_id>/generate-now/",
                self.admin_site.admin_view(self.generate_now_view),
                name="audioconversionrequest-generate-now",
            )
        ]
        return custom + urls

    def generate_now_view(self, request, object_id):
        obj = AudioConversionRequest.objects.filter(pk=object_id).first()
        if not obj:
            self.message_user(request, "Demande introuvable.", level="error")
            return redirect("..")
        if obj.paiement_requis and obj.statut != "paid":
            self.message_user(request, "Paiement non validé. Impossible de générer.", level="error")
            return redirect("..")
        if obj.audio:
            self.message_user(request, "Audio déjà généré.", level="warning")
            return redirect("..")
        try:
            self._generate_audio_for_obj(obj)
            self.message_user(request, "Audio généré avec succès.")
        except Exception as exc:
            obj.statut = "error"
            obj.async_error = str(exc)
            obj.save(update_fields=["statut", "async_error", "updated_at"])
            self.message_user(request, f"Erreur génération: {exc}", level="error")
        return redirect("..")

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            extra_context["generate_now_url"] = f"{object_id}/generate-now/"
        return super().changeform_view(request, object_id, form_url, extra_context)

    def paiement_initie(self, obj):
        return bool(obj.paiement_initie_at)

    paiement_initie.boolean = True
    paiement_initie.short_description = "Paiement initié"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        start_raw = request.GET.get("created_from", "")
        end_raw = request.GET.get("created_to", "")
        start_date = parse_date(start_raw) if start_raw else None
        end_date = parse_date(end_raw) if end_raw else None
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        return queryset

    def _generate_audio_for_obj(self, obj):
        from gtts import gTTS
        from django.core.files.base import ContentFile
        from django.utils.text import slugify
        import uuid

        text = obj.texte or ""
        if obj.fichier and not text.strip():
            text = extract_text_from_file(
                obj.fichier,
                language_hint=obj.langue,
                force_ocr=obj.force_ocr,
            )
            if text and not obj.texte:
                obj.texte = text
                obj.save(update_fields=["texte", "updated_at"])
        if not text.strip():
            raise RuntimeError("Texte vide après extraction.")
        if obj.langue == "auto":
            detected = detect_tts_language(text, selected="auto")
            if detected and detected != obj.langue:
                obj.langue = detected
                obj.save(update_fields=["langue", "updated_at"])
        appearance = SiteAppearance.objects.first()
        normalized_text = normalize_tts_text(
            text,
            appearance=appearance,
            use_original=obj.use_original_text,
        )
        if normalized_text and normalized_text != text:
            obj.texte_normalise = normalized_text
            obj.save(update_fields=["texte_normalise", "updated_at"])
        tts = gTTS(normalized_text or text, lang="fr", slow=False)
        audio_bytes = ContentFile(b"")
        filename = f"conversion-{slugify(obj.email) or obj.id}-{uuid.uuid4().hex}.mp3"
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        obj.audio.save(filename, audio_bytes, save=False)
        obj.statut = "delivered"
        obj.save(update_fields=["audio", "statut", "updated_at"])

    def convertir_fichier_en_audio(self, request, queryset):
        import requests

        success = 0
        failures = 0
        try:
            requests.get("https://translate.google.com", timeout=5)
        except Exception:
            self.message_user(request, "Connexion Internet indisponible. Impossible de générer l'audio.", level="error")
            return
        for obj in queryset:
            if not obj.fichier and not obj.texte:
                self.message_user(request, f"Aucun texte/fichier pour la demande #{obj.id}.", level="warning")
                continue
            try:
                obj.statut = "processing"
                obj.async_error = ""
                obj.save(update_fields=["statut", "async_error", "updated_at"])
                self._generate_audio_for_obj(obj)
                success += 1
            except Exception as exc:
                failures += 1
                obj.statut = "error"
                obj.async_error = str(exc)
                obj.save(update_fields=["statut", "async_error", "updated_at"])
                self.message_user(request, f"Erreur pour la demande #{obj.id}: {exc}", level="error")
        if success:
            self.message_user(request, f"{success} fichier(s) converti(s) avec succès.", level="success")
        if failures and not success:
            self.message_user(request, "Aucune conversion n'a abouti. Vérifiez les erreurs ci-dessus.", level="error")

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


@admin.register(AudioConversionGenerated)
class AudioConversionGeneratedAdmin(AudioConversionRequestAdmin):
    """Liste dédiée des audios générés."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(audio__isnull=False).exclude(audio="")

    def marquer_paye_et_envoyer(self, request, queryset):
        from django.core.mail import EmailMessage
        import requests

        appearance = SiteAppearance.objects.first()
        from_email = appearance.site_email if appearance and appearance.site_email else None

        success = 0
        failures = 0
        try:
            requests.get("https://translate.google.com", timeout=5)
        except Exception:
            self.message_user(request, "Connexion Internet indisponible. Impossible de générer l'audio.", level="error")
            return

        for obj in queryset:
            if not obj.email:
                self.message_user(request, f"Aucun email pour la demande #{obj.id}.", level="warning")
                continue
            try:
                obj.statut = "paid"
                obj.save(update_fields=["statut", "updated_at"])
                if not obj.audio:
                    self._generate_audio_for_obj(obj)
                email = EmailMessage(
                    "Votre audio est prêt",
                    "Bonjour,\n\nVotre conversion audio est prête. Vous trouverez le fichier MP3 en pièce jointe.\n\nEditions Recréation",
                    from_email,
                    [obj.email],
                )
                if obj.audio and obj.audio.path:
                    email.attach_file(obj.audio.path)
                email.send(fail_silently=True)
                success += 1
            except Exception as exc:
                failures += 1
                obj.statut = "error"
                obj.async_error = str(exc)
                obj.save(update_fields=["statut", "async_error", "updated_at"])
                self.message_user(request, f"Erreur pour la demande #{obj.id}: {exc}", level="error")

        if success:
            self.message_user(request, f"{success} demande(s) traitée(s) et envoyée(s).", level="success")
        if failures and not success:
            self.message_user(request, "Aucun envoi n'a abouti. Vérifiez les erreurs ci-dessus.", level="error")

    marquer_paye_et_envoyer.short_description = "Marquer payé + générer + envoyer par email"

    def changelist_view(self, request, extra_context=None):
        from django.utils import timezone
        from django.db.models import Count, Q
        from django.db.models.functions import TruncDate

        extra_context = extra_context or {}
        qs = self.get_queryset(request)
        now = timezone.now()
        last_30 = now - timezone.timedelta(days=30)

        extra_context["stats"] = {
            "total": qs.count(),
            "gratuits": qs.filter(paiement_requis=False).count(),
            "payants": qs.filter(paiement_requis=True).count(),
            "paiement_initie": qs.filter(paiement_initie_at__isnull=False).count(),
            "audios": qs.filter(audio__isnull=False).count(),
        }

        daily = (
            qs.filter(created_at__date__gte=last_30.date())
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total=Count("id"), payants=Count("id", filter=Q(paiement_requis=True)))
            .order_by("day")
        )
        extra_context["daily"] = list(daily)
        extra_context["daily_from"] = last_30.date()
        extra_context["daily_to"] = now.date()
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(MessageContact)
class MessageContactAdmin(ModelAdmin):
    formfield_overrides = {
        RichTextField: {"widget": CKEditor5Widget(config_name="extends")},
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

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in {"message", "notes_admin"}:
            config = "ultra_simple" if db_field.name == "notes_admin" else "simple"
            kwargs["widget"] = CKEditor5Widget(config_name=config)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(SoumissionManuscrit)
class SoumissionManuscritAdmin(ModelAdmin):
    formfield_overrides = {
        RichTextField: {"widget": CKEditor5Widget(config_name="extends")},
    }
    list_display = ("titre_ouvrage", "nom_auteur", "nom_complet", "type_contrat", "nationalite", "pays_residence", "whatsapp", "audio_link", "created_at")
    list_filter = ("created_at",)
    search_fields = ("titre_ouvrage", "nom_auteur", "nom_complet", "whatsapp", "autre_numero", "nationalite", "pays_residence")
    readonly_fields = ("created_at", "updated_at", "audio_link")

    fieldsets = (
        ("Identité", {"fields": ("nom_complet", "nom_auteur", "whatsapp", "autre_numero", "nationalite", "pays_residence")}),
        ("Ouvrage", {"fields": ("titre_ouvrage", "genre_litteraire", "type_contrat", "synopsis", "avantages", "inconvenients")}),
        ("Fichiers", {"fields": ("fichier_ouvrage", "photo_auteur", "carte_identite")}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    def audio_link(self, obj):
        if obj.audio_request and obj.audio_request.audio:
            return format_html('<a href="{}" target="_blank">?couter / T?l?charger</a>', obj.audio_request.audio.url)
        return '-'

    audio_link.short_description = 'Audio'




# -------------------------------------------------------------------------------
# ADMIN: MEDIA CLEANUP
# -------------------------------------------------------------------------------

def _list_media_files():
    media_root = getattr(settings, "MEDIA_ROOT", None)
    if not media_root or not os.path.isdir(media_root):
        return []
    media_url = getattr(settings, "MEDIA_URL", "/media/")
    files = []
    for root, _, filenames in os.walk(media_root):
        for name in filenames:
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, media_root)
            try:
                size = os.path.getsize(full_path)
            except OSError:
                size = 0
            try:
                mtime = os.path.getmtime(full_path)
            except OSError:
                mtime = 0
            ext = os.path.splitext(name)[1].lower()
            file_type = "other"
            if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                file_type = "image"
            elif ext in {".mp3", ".wav", ".m4a", ".ogg"}:
                file_type = "audio"
            elif ext in {".pdf"}:
                file_type = "pdf"
            rel_web = rel_path.replace("\\", "/")
            file_url = f"{media_url}{rel_web}"
            files.append({"path": rel_web, "size": size, "mtime": mtime})
            files[-1].update({"type": file_type, "url": file_url})
    return sorted(files, key=lambda f: f["path"].lower())


def media_cleanup_view(request):
    files = _list_media_files()
    if request.method == "POST":
        selected = request.POST.getlist("paths")
        media_root = getattr(settings, "MEDIA_ROOT", None)
        deleted = 0
        if media_root:
            for rel in selected:
                rel = rel.replace("\\", "/")
                full_path = os.path.abspath(os.path.join(media_root, rel))
                if not full_path.startswith(os.path.abspath(media_root)):
                    continue
                if os.path.isfile(full_path):
                    try:
                        os.remove(full_path)
                        deleted += 1
                    except OSError:
                        continue
        if deleted:
            messages.success(request, f"{deleted} fichier(s) supprimé(s).")
        return redirect("admin:media-cleanup")
    return render(
        request,
        "admin/media_cleanup.html",
        {"files": files, "media_root": getattr(settings, "MEDIA_ROOT", "")},
    )


def _patch_admin_urls():
    orig_get_urls = admin.site.get_urls

    def get_urls():
        urls = orig_get_urls()
        custom = [
            path(
                "media-cleanup/",
                admin.site.admin_view(media_cleanup_view),
                name="media-cleanup",
            )
        ]
        return custom + urls

    admin.site.get_urls = get_urls


_patch_admin_urls()
