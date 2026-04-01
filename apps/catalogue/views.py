"""
FICHIER : apps/catalogue/views.py
"""

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.contrib.auth import login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.db import close_old_connections
from django.contrib.auth.views import LoginView as DjangoLoginView, PasswordResetView as DjangoPasswordResetView
from datetime import date
import unicodedata

from .forms import ContactForm, NewsletterForm, SoumissionManuscritForm, AudioConversionForm, AudioConversionHumanForm, CommitteeSignupForm, ManuscriptReviewForm, StyledSignupForm, StyledLoginForm
from .utils.audio_conversion import (
    estimate_pages_from_text,
    count_pages_for_file,
    extract_text_from_file,
    normalize_tts_text,
    detect_tts_language,
)
from .models import (
    Actualite,
    Auteur,
    Collection,
    InscriptionNewsletter,
    Livre,
    Membre,
    MessageContact,
    Nationalite,
    Page,
    PageBlock,
    PrixLitteraire,
    AudioConversionRequest,
    SoumissionManuscrit,
    ManuscriptReview,
    CommitteeApplication,
)
from apps.core.models import SiteAppearance, SiteContent


# -------------------------------------------------------------------------------
# OUTILS DE RECHERCHE (INSENSIBLE AUX ACCENTS)
# -------------------------------------------------------------------------------

def _normalize_text(value):
    if value is None:
        return ""
    value = str(value).lower()
    normalized = unicodedata.normalize("NFD", value)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _text_contains(normalized_query, *values):
    if not normalized_query:
        return False
    for value in values:
        if normalized_query in _normalize_text(value):
            return True
    return False


def _get_site_content():
    return SiteContent.objects.first()


def _content_value(content, field_name, default):
    value = getattr(content, field_name, None) if content else None
    return value or default


# -------------------------------------------------------------------------------
# PAGE D'ACCUEIL AVEC NEWSLETTER
# -------------------------------------------------------------------------------

class IndexView(TemplateView):
    """Vue page d'accueil avec formulaire newsletter."""

    template_name = "catalogue/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page = Page.objects.filter(slug="accueil", is_active=True).first()
        context["page"] = page
        context["page_blocks"] = (
            page.blocks.filter(est_actif=True)
            .prefetch_related("items")
            .order_by("ordre")
            if page
            else []
        )
        if page and page.meta_title:
            context["page_title"] = page.meta_title
        if page and page.meta_description:
            context["page_description"] = page.meta_description
        if page and getattr(page, "meta_keywords", ""):
            context["page_keywords"] = getattr(page, "meta_keywords", "")

        context["livres_carousel"] = (
            Livre.objects.filter(est_publie=True).prefetch_related("auteurs").order_by("-parution")
        )
        context["nouveautes"] = (
            Livre.objects.filter(est_publie=True, est_nouveau=True).prefetch_related("auteurs").order_by("-parution")[:12]
        )
        context["bestsellers"] = (
            Livre.objects.filter(est_publie=True, est_bestseller=True).prefetch_related("auteurs").order_by("-parution")[:8]
        )
        context["prochaines_parutions"] = (
            Livre.objects.filter(est_publie=True, est_prochaine_parution=True).prefetch_related("auteurs").order_by("parution")[:8]
        )
        context["actualites_ticker"] = (
            Actualite.objects.filter(est_publie=True).order_by("-date_publication")[:10]
        )

        context["form"] = NewsletterForm()
        if "page_title" not in context:
            context["page_title"] = "Accueil | Editions Recr\u00e9ation | Maison d'\u00e9dition g\u00e9n\u00e9raliste"
        last_id = self.request.session.pop("audio_request_id", None)
        if last_id:
            context["last_request"] = AudioConversionRequest.objects.filter(id=last_id).first()
        return context

    def post(self, request, *args, **kwargs):
        form = NewsletterForm(request.POST)
        content = _get_site_content()
        if form.is_valid():
            email = form.cleaned_data["email"]
            inscription, created = InscriptionNewsletter.objects.get_or_create(
                email=email,
                defaults={"est_actif": True},
            )
            if created:
                messages.success(
                    request,
                    _content_value(
                        content,
                        "newsletter_message_success",
                        "Merci ! Vous \u00eates inscrit \u00e0 notre newsletter.",
                    ),
                )
            else:
                if not inscription.est_actif:
                    inscription.est_actif = True
                    inscription.save(update_fields=["est_actif", "updated_at"])
                    messages.success(
                        request,
                        _content_value(
                            content,
                            "newsletter_message_reactivated",
                            "Votre inscription a \u00e9t\u00e9 r\u00e9activ\u00e9e.",
                        ),
                    )
                else:
                    messages.info(
                        request,
                        _content_value(
                            content,
                            "newsletter_message_already",
                            "Vous \u00eates d\u00e9j\u00e0 inscrit.",
                        ),
                    )
        else:
            messages.error(
                request,
                _content_value(
                    content,
                    "newsletter_message_error",
                    "Une erreur s'est produite. Veuillez v\u00e9rifier votre email.",
                ),
            )

        return redirect("catalogue:index")


# -------------------------------------------------------------------------------
# CATALOGUE
# -------------------------------------------------------------------------------

class CatalogueView(ListView):
    """Vue liste catalogue."""

    model = Livre
    template_name = "catalogue/catalogue.html"
    context_object_name = "livres"
    paginate_by = 12

    def get_queryset(self):
        queryset = Livre.objects.filter(est_publie=True).prefetch_related("auteurs", "collection")

        recherche = self.request.GET.get("search", "").strip()
        categorie = self.request.GET.get("categorie", "").strip()
        collection = self.request.GET.get("collection", "").strip()
        version = self.request.GET.get("version", "").strip().lower()
        langue = self.request.GET.get("langue", "").strip().lower()
        sort = self.request.GET.get("sort", "-parution").strip()

        if categorie and categorie != "tous":
            queryset = queryset.filter(categorie=categorie)

        if collection:
            queryset = queryset.filter(collection__slug=collection)
        
        if version == "papier":
            queryset = queryset.filter(version_papier=True)
        elif version == "numerique":
            queryset = queryset.filter(version_numerique=True)
        elif version == "audio":
            queryset = queryset.filter(version_audio=True)
        
        if langue:
            queryset = queryset.filter(langue_publication=langue)

        sort_map = {
            "-parution": "-parution",
            "parution": "parution",
            "titre": "titre",
            "auteur": "auteurs__nom",
        }
        queryset = queryset.order_by(sort_map.get(sort, "-parution")).distinct()

        if recherche:
            normalized_query = _normalize_text(recherche)
            livres_list = []
            for livre in queryset:
                auteurs_noms = " ".join(auteur.nom for auteur in livre.auteurs.all())
                collection_nom = livre.collection.nom if livre.collection else ""
                if _text_contains(
                    normalized_query,
                    livre.titre,
                    auteurs_noms,
                    livre.isbn,
                    collection_nom,
                ):
                    livres_list.append(livre)
            return livres_list

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        version_actuelle = self.request.GET.get("version", "").strip().lower()
        context["recherche"] = self.request.GET.get("search", "")
        context["categorie_actuelle"] = self.request.GET.get("categorie", "")
        context["collection_actuelle"] = self.request.GET.get("collection", "")
        context["version_actuelle"] = version_actuelle
        context["langue_actuelle"] = self.request.GET.get("langue", "")
        context["langues_list"] = Livre.LANGUES
        context["sort_actuel"] = self.request.GET.get("sort", "-parution")
        queryset_or_list = self.get_queryset()
        if isinstance(queryset_or_list, list):
            context["total_livres"] = len(queryset_or_list)
        else:
            context["total_livres"] = queryset_or_list.count()
        context["page_title"] = "Catalogue - Editions Recr\u00e9ation"
        
        livres_page = context.get("livres")
        if livres_page:
            for livre in livres_page:
                livre.image_affichage = livre.image_pour_version(version_actuelle)
        return context


class LivresNumeriquesView(CatalogueView):
    """Vue liste livres numériques."""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(version_numerique=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_heading"] = "Livres numériques"
        context["page_subtitle"] = "Découvrez nos ouvrages disponibles en version numérique"
        context["page_title"] = "Livres numériques - Editions Recréation"
        context["version_actuelle"] = "numerique"
        livres_page = context.get("livres")
        if livres_page:
            for livre in livres_page:
                livre.image_affichage = livre.image_pour_version("numerique")
        return context


class LivresAudioView(CatalogueView):
    """Vue liste livres audio."""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(version_audio=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_heading"] = "Livres audio"
        context["page_subtitle"] = "Explorez nos livres disponibles en version audio"
        context["page_title"] = "Livres audio - Editions Recréation"
        context["version_actuelle"] = "audio"
        livres_page = context.get("livres")
        if livres_page:
            for livre in livres_page:
                livre.image_affichage = livre.image_pour_version("audio")
        return context


class LivresPapierView(CatalogueView):
    """Vue liste livres papier."""

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(version_papier=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_heading"] = "Livres papier"
        context["page_subtitle"] = "Découvrez nos ouvrages disponibles en version papier"
        context["page_title"] = "Livres papier - Editions Recréation"
        context["version_actuelle"] = "papier"
        livres_page = context.get("livres")
        if livres_page:
            for livre in livres_page:
                livre.image_affichage = livre.image_pour_version("papier")
        return context


class LivreDetailView(DetailView):
    """Vue detail livre."""

    model = Livre
    template_name = "catalogue/livre_detail.html"
    context_object_name = "livre"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Livre.objects.filter(est_publie=True).prefetch_related("auteurs")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        livre = self.get_object()

        context["livres_suggeres"] = (
            Livre.objects.filter(
                Q(auteurs__in=livre.auteurs.all()) | Q(categorie=livre.categorie),
                est_publie=True,
            )
            .exclude(pk=livre.pk)
            .prefetch_related("auteurs")
            .distinct()[:4]
        )

        categorie_code = (livre.categorie or "").lower().strip()
        categorie_label = livre.get_categorie_display() or ""

        code_to_label = {
            "poemes": "Po\u00e8mes",
            "litterature-fr": "Litt\u00e9rature fran\u00e7aise",
            "litterature-etr": "Litt\u00e9rature \u00e9trang\u00e8re",
            "policiers": "Polars/Thrillers",
        }
        broken_to_label = {
            "po\u00e3\u00a8mes": "Po\u00e8mes",
            "po\u010dmes": "Po\u00e8mes",
            "po?mes": "Po\u00e8mes",
            "litt\u00e3\u00a9rature fran\u00e3\u00a7aise": "Litt\u00e9rature fran\u00e7aise",
            "litt\u00e3\u00a9rature \u00e3\u00a9trang\u00e3\u00a8re": "Litt\u00e9rature \u00e9trang\u00e8re",
        }

        context["categorie_label"] = code_to_label.get(
            categorie_code,
            broken_to_label.get(categorie_label.lower(), categorie_label),
        )

        context["collection_label"] = livre.collection.nom if livre.collection else ""

        context["page_title"] = f"{livre.titre} - Editions Recr\u00e9ation"
        return context


# -------------------------------------------------------------------------------
# AUTEURS
# -------------------------------------------------------------------------------

class AuteursView(ListView):
    """Vue liste auteurs."""

    model = Auteur
    template_name = "catalogue/auteurs.html"
    context_object_name = "auteurs"

    def get_queryset(self):
        queryset = Auteur.objects.avec_livres().prefetch_related("nationalites").all()
        nat_id = self.request.GET.get("nationalite", "").strip()
        if nat_id:
            queryset = queryset.filter(nationalites__id=nat_id)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nationalites"] = Nationalite.objects.all().order_by("nom")
        context["nationalite_actuelle"] = self.request.GET.get("nationalite", "")
        context["page_title"] = "Nos Auteurs - Editions Recr\u00e9ation"
        return context


class AuteurDetailView(DetailView):
    """Vue detail auteur."""

    model = Auteur
    template_name = "catalogue/auteur_detail.html"
    context_object_name = "auteur"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auteur = self.get_object()
        context["livres"] = auteur.livres.filter(est_publie=True).prefetch_related("auteurs").order_by("-parution")
        context["nombre_livres"] = context["livres"].count()
        context["page_title"] = f"{auteur.nom} - Editions Recr\u00e9ation"
        return context


class MembreDetailView(DetailView):
    """Vue detail membre de l'équipe."""

    model = Membre
    template_name = "catalogue/membre_detail.html"
    context_object_name = "membre"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return Membre.objects.filter(est_actif=True).prefetch_related("nationalites")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membre = self.get_object()
        context["page_title"] = f"{membre.nom_complet} - Editions Recr\u00e9ation"
        return context


# -------------------------------------------------------------------------------
# CONTACT
# -------------------------------------------------------------------------------

class ContactView(FormView):
    """Vue page contact avec formulaire."""

    template_name = "catalogue/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("catalogue:contact")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = Page.objects.filter(slug="contact", is_active=True).first()
        context["page"] = page
        context["page_blocks"] = (
            page.blocks.filter(est_actif=True)
            .prefetch_related("items")
            .order_by("ordre")
            if page
            else []
        )
        if page and page.meta_title:
            context["page_title"] = page.meta_title
        else:
            context["page_title"] = "Contact - Editions Recr\u00e9ation"
        if page and page.meta_description:
            context["page_description"] = page.meta_description
        if page and getattr(page, "meta_keywords", ""):
            context["page_keywords"] = getattr(page, "meta_keywords", "")
        return context

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            _content_value(
                _get_site_content(),
                "contact_message_success",
                "Votre message a \u00e9t\u00e9 envoy\u00e9 avec succ\u00e8s ! Nous vous r\u00e9pondrons dans les plus brefs d\u00e9lais.",
            ),
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            _content_value(
                _get_site_content(),
                "contact_message_error",
                "Une erreur s'est produite. Veuillez v\u00e9rifier les informations saisies.",
            ),
        )
        return super().form_invalid(form)


# -------------------------------------------------------------------------------
# A PROPOS
# -------------------------------------------------------------------------------

class AProposView(TemplateView):
    """Vue page a propos."""

    template_name = "catalogue/a-propos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["membres"] = Membre.objects.filter(est_actif=True).prefetch_related("nationalites").order_by("ordre_affichage")
        context["livres_count"] = Livre.objects.filter(est_publie=True).count()
        auteurs_publies = Auteur.objects.filter(livres__est_publie=True).distinct()
        context["auteurs_count"] = auteurs_publies.count()
        context["pays_count"] = Nationalite.objects.filter(auteurs__in=auteurs_publies).distinct().count()
        context["prix_litteraires_count"] = PrixLitteraire.objects.filter(est_actif=True).count()
        start = date(2023, 12, 1)
        today = date.today()
        years_elapsed = today.year - start.year - ((today.month, today.day) < (start.month, start.day))
        context["annees_experience"] = f"{max(1, years_elapsed)}+"
        page = Page.objects.filter(slug="a-propos", is_active=True).first()
        context["page"] = page
        context["page_blocks"] = (
            page.blocks.filter(est_actif=True)
            .prefetch_related("items")
            .order_by("ordre")
            if page
            else []
        )
        context["page_title"] = page.meta_title if page and page.meta_title else "\u00c0 Propos - Editions Recr\u00e9ation"
        if page and page.meta_description:
            context["page_description"] = page.meta_description
        if page and getattr(page, "meta_keywords", ""):
            context["page_keywords"] = getattr(page, "meta_keywords", "")
        return context


# -------------------------------------------------------------------------------
# COLLECTIONS
# -------------------------------------------------------------------------------

class CollectionDetailView(DetailView):
    """Vue detail collection."""

    model = Collection
    template_name = "catalogue/collection_detail.html"
    context_object_name = "collection"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Collection.objects.filter(est_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection = self.get_object()
        livres = (
            collection.livres.filter(est_publie=True)
            .prefetch_related("auteurs")
            .order_by("-parution")
        )
        auteurs = Auteur.objects.filter(livres__collection=collection, livres__est_publie=True).distinct().order_by("nom")

        context.update(
            {
                "livres": livres,
                "auteurs_collection": auteurs,
                "page_title": collection.meta_title if collection.meta_title else f"{collection.nom} - Editions Recréation",
                "page_description": collection.meta_description if collection.meta_description else None,
            "page_keywords": getattr(collection, "meta_keywords", "") if getattr(collection, "meta_keywords", None) else "",
            }
        )
        return context


class NosContratsView(TemplateView):
    """Vue page nos contrats."""

    template_name = "catalogue/nos-contrats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = Page.objects.filter(slug="nos-contrats", is_active=True).first()
        context["page"] = page
        context["page_blocks"] = (
            page.blocks.filter(est_actif=True)
            .prefetch_related("items")
            .order_by("ordre")
            if page
            else []
        )
        context["page_title"] = page.meta_title if page and page.meta_title else "Nos Contrats - Editions Recr\u00e9ation"
        if page and page.meta_description:
            context["page_description"] = page.meta_description
        if page and getattr(page, "meta_keywords", ""):
            context["page_keywords"] = getattr(page, "meta_keywords", "")
        return context


class SoumissionManuscritView(FormView):
    """Vue page soumission de manuscrit."""

    template_name = "catalogue/soumission-manuscrit.html"
    form_class = SoumissionManuscritForm
    success_url = reverse_lazy("catalogue:soumission-manuscrit")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context.get("site_content") and context["site_content"].soumission_meta_keywords:
            context["page_keywords"] = context["site_content"].soumission_meta_keywords
        return context

    def form_valid(self, form):
        submission = form.save()
        audio_request = None
        try:
            audio_request = AudioConversionRequest.objects.create(
                email="",
                whatsapp=submission.whatsapp or "",
                texte="",
                fichier=submission.fichier_ouvrage,
                langue="auto",
                voix="standard",
                voice_type="synthetic",
                paiement_requis=False,
                statut="processing",
            )
            submission.audio_request = audio_request
            submission.save(update_fields=["audio_request", "updated_at"])

            from .tasks import convert_audio_request
            convert_audio_request(audio_request.id)
        except Exception as exc:
            if audio_request:
                audio_request.statut = "error"
                audio_request.async_error = str(exc)
                audio_request.save(update_fields=["statut", "async_error", "updated_at"])

        messages.success(
            self.request,
            _content_value(
                _get_site_content(),
                "soumission_message_success",
                "Merci ! Votre manuscrit a ?t? soumis avec succ?s. Nous vous contacterons rapidement.",
            ),
        )
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(
            self.request,
            _content_value(
                _get_site_content(),
                "soumission_message_error",
                "Une erreur s'est produite. Veuillez v\u00e9rifier les informations saisies.",
            ),
        )
        return super().form_invalid(form)


class LegalView(TemplateView):
    """Vue page mentions l\u00e9gales."""

    template_name = "catalogue/legal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug_map = {
            "mentions-legales": "mentions-legales",
            "confidentialite": "confidentialite",
            "cookies": "cookies",
        }
        url_name = self.request.resolver_match.url_name
        slug = slug_map.get(url_name, "mentions-legales")
        page = Page.objects.filter(slug=slug, is_active=True).first()
        context["page"] = page
        context["page_blocks"] = (
            page.blocks.filter(est_actif=True)
            .prefetch_related("items")
            .order_by("ordre")
            if page
            else []
        )
        if page and page.meta_title:
            context["page_title"] = page.meta_title
        else:
            titles = {
                "mentions-legales": "Mentions l\u00e9gales - Editions Recr\u00e9ation",
                "confidentialite": "Confidentialit\u00e9 - Editions Recr\u00e9ation",
                "cookies": "Cookies - Editions Recr\u00e9ation",
            }
            context["page_title"] = titles.get(slug, "Mentions l\u00e9gales - Editions Recr\u00e9ation")
        if page and page.meta_description:
            context["page_description"] = page.meta_description
        if page and getattr(page, "meta_keywords", ""):
            context["page_keywords"] = getattr(page, "meta_keywords", "")
        return context


class PageDetailView(DetailView):
    """Vue page dynamique."""
    
    model = Page
    template_name = "catalogue/page.html"
    context_object_name = "page"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    def get_queryset(self):
        return Page.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context.get("page")
        context["page_blocks"] = (
            page.blocks.filter(est_actif=True)
            .prefetch_related("items")
            .order_by("ordre")
            if page
            else []
        )
        if page and page.meta_title:
            context["page_title"] = page.meta_title
        else:
            context["page_title"] = f"{page.title} - Editions Recr\u00e9ation" if page else "Editions Recr\u00e9ation"
        if page and page.meta_description:
            context["page_description"] = page.meta_description
        if page and getattr(page, "meta_keywords", ""):
            context["page_keywords"] = getattr(page, "meta_keywords", "")
        return context




class SearchView(TemplateView):
    """Vue page recherche globale."""

    template_name = "catalogue/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()

        livres = []
        auteurs = []
        membres = []
        actualites = []
        pages = []

        if query:
            normalized_query = _normalize_text(query)

            livres_candidates = (
                Livre.objects.filter(est_publie=True)
                .prefetch_related("auteurs", "collection")
                .order_by("-parution")
            )
            livres = []
            for livre in livres_candidates:
                auteurs_noms = " ".join(auteur.nom for auteur in livre.auteurs.all())
                collection_nom = livre.collection.nom if livre.collection else ""
                if _text_contains(
                    normalized_query,
                    livre.titre,
                    auteurs_noms,
                    livre.isbn,
                    collection_nom,
                    livre.resume,
                ):
                    livres.append(livre)
                if len(livres) >= 20:
                    break

            auteurs_candidates = Auteur.objects.prefetch_related("nationalites").order_by("nom")
            auteurs = []
            for auteur in auteurs_candidates:
                nationalites = " ".join(n.nom for n in auteur.nationalites.all())
                if _text_contains(
                    normalized_query,
                    auteur.nom,
                    auteur.specialite,
                    auteur.biographie,
                    nationalites,
                ):
                    auteurs.append(auteur)
                if len(auteurs) >= 20:
                    break

            membres_candidates = Membre.objects.prefetch_related("nationalites").order_by("ordre_affichage")
            membres = []
            for membre in membres_candidates:
                nationalites = " ".join(n.nom for n in membre.nationalites.all())
                if _text_contains(
                    normalized_query,
                    membre.nom_complet,
                    membre.poste,
                    membre.biographie,
                    nationalites,
                ):
                    membres.append(membre)
                if len(membres) >= 20:
                    break

            actualites_candidates = Actualite.objects.filter(est_publie=True).order_by("-date_publication")
            actualites = []
            for actualite in actualites_candidates:
                if _text_contains(
                    normalized_query,
                    actualite.titre,
                    actualite.extrait,
                    actualite.contenu,
                ):
                    actualites.append(actualite)
                if len(actualites) >= 20:
                    break

            pages_candidates = [
                {"title": "Accueil", "url": reverse_lazy("catalogue:index"), "keywords": "accueil home"},
                {"title": "\u00c0 propos", "url": reverse_lazy("catalogue:a-propos"), "keywords": "a propos histoire mission"},
                {"title": "Catalogue", "url": reverse_lazy("catalogue:catalogue"), "keywords": "catalogue livres"},
                {"title": "Conversion de texte en audio", "url": reverse_lazy("catalogue:conversion-audio"), "keywords": "conversion texte audio tts"},
                {"title": "Livres numériques", "url": reverse_lazy("catalogue:livres-numeriques"), "keywords": "livres numeriques ebook"},
                {"title": "Livres audio", "url": reverse_lazy("catalogue:livres-audio"), "keywords": "livres audio audiobook"},
                {"title": "Auteurs", "url": reverse_lazy("catalogue:auteurs"), "keywords": "auteurs \u00e9crivains"},
                {"title": "Actualit\u00e9s", "url": reverse_lazy("catalogue:actualites"), "keywords": "actualites news"},
                {"title": "Nos contrats", "url": reverse_lazy("catalogue:nos-contrats"), "keywords": "contrats publication"},
                {"title": "Contrat à Compte d'Éditeur", "url": reverse_lazy("catalogue:nos-contrats"), "keywords": "compte editeur"},
                {"title": "Contrat à Compte d'Auteur", "url": reverse_lazy("catalogue:nos-contrats"), "keywords": "compte auteur"},
                {"title": "Contrat à Compte Particitatif", "url": reverse_lazy("catalogue:nos-contrats"), "keywords": "compte participatif particitatif"},
                {"title": "Contact", "url": reverse_lazy("catalogue:contact"), "keywords": "contact email telephone"},
                {"title": "Mentions l\u00e9gales", "url": reverse_lazy("catalogue:mentions-legales"), "keywords": "mentions legales conditions"},
                {"title": "Confidentialit\u00e9", "url": reverse_lazy("catalogue:confidentialite"), "keywords": "confidentialite donnees"},
                {"title": "Cookies", "url": reverse_lazy("catalogue:cookies"), "keywords": "cookies"},
                {"title": "Soumettre un manuscrit", "url": reverse_lazy("catalogue:soumission-manuscrit"), "keywords": "soumettre manuscrit"},
            ]

            lowered = _normalize_text(query)
            pages = [
                page for page in pages_candidates
                if lowered in _normalize_text(page["title"]) or lowered in _normalize_text(page["keywords"])
            ]

        total_results = len(livres) + len(auteurs) + len(membres) + len(actualites) + len(pages)

        context.update(
            {
                "query": query,
                "livres": livres,
                "auteurs": auteurs,
                "membres": membres,
                "actualites": actualites,
                "pages": pages,
                "total_results": total_results,
                "page_title": "Recherche - Editions Recr\u00e9ation",
            }
        )

        return context


# -------------------------------------------------------------------------------
# ACTUALITES
# -------------------------------------------------------------------------------

class ActualitesView(ListView):
    """Vue liste actualites."""

    model = Actualite
    template_name = "catalogue/actualites.html"
    context_object_name = "actualites"
    paginate_by = 9

    def get_queryset(self):
        qs = Actualite.objects.filter(est_publie=True).order_by("-est_une_a_la_une", "-date_publication")
        filtre = self.request.GET.get("filtre", "tous")
        annee = self.request.GET.get("annee", "")
        mois = self.request.GET.get("mois", "")
        if filtre == "a-la-une":
            qs = qs.filter(est_une_a_la_une=True)
        if annee:
            qs = qs.filter(date_publication__year=annee)
        if mois:
            try:
                qs = qs.filter(date_publication__month=int(mois))
            except ValueError:
                pass
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Actualit\u00e9s - Editions Recr\u00e9ation"
        context["filtre_actuel"] = self.request.GET.get("filtre", "tous")
        context["annee_actuelle"] = self.request.GET.get("annee", "")
        context["mois_actuel"] = self.request.GET.get("mois", "")
        context["annees_actualites"] = (
            Actualite.objects.filter(est_publie=True)
            .dates("date_publication", "year", order="DESC")
            .values_list("date_publication__year", flat=True)
        )
        return context


class CollectionsView(TemplateView):
    """Vue liste des collections."""

    template_name = "catalogue/collections.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collections = Collection.objects.filter(est_active=True).order_by("ordre_affichage", "nom")
        context["collections"] = collections
        context["page_title"] = "Collections - Editions Récréation"
        return context


class ActualiteDetailView(DetailView):
    """Vue detail actualite."""

    model = Actualite
    template_name = "catalogue/actualite_detail.html"
    context_object_name = "actualite"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Actualite.objects.filter(est_publie=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        actualite = self.get_object()
        context["actualites_suggeres"] = (
            Actualite.objects.filter(est_publie=True)
            .exclude(pk=actualite.pk)
            .order_by("-date_publication")[:3]
        )
        context["page_title"] = f"{actualite.titre} - Editions Recr\u00e9ation"
        return context


# -------------------------------------------------------------------------------
# CONVERSION TEXTE EN AUDIO
# -------------------------------------------------------------------------------

FREE_TEXT_LIMIT = 5000


class AudioConversionChoiceView(TemplateView):
    template_name = "catalogue/conversion-audio-choice.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context.get("site_content") and context["site_content"].conversion_meta_keywords:
            context["page_keywords"] = context["site_content"].conversion_meta_keywords
        return context


class AudioConversionHumanView(FormView):
    template_name = "catalogue/conversion-audio-humain.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context.get("site_content") and context["site_content"].conversion_meta_keywords:
            context["page_keywords"] = context["site_content"].conversion_meta_keywords
        return context
    form_class = AudioConversionHumanForm
    success_url = reverse_lazy("catalogue:conversion-audio-humain")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = Page.objects.filter(slug="conversion-texte-audio", is_active=True).first()
        context["page"] = page
        context["page_title"] = "Conversion de texte en audio (voix humaine) - Editions Récréation"
        return context

    def form_valid(self, form):
        texte = (form.cleaned_data.get("texte") or "").strip()
        fichier = form.cleaned_data.get("fichier")

        demande = form.save(commit=False)
        demande.voice_type = "human"
        demande.paiement_requis = True
        demande.statut = "awaiting_payment"

        if fichier:
            pages_count = count_pages_for_file(
                fichier,
                language_hint=demande.langue,
                force_ocr=demande.force_ocr,
            )
        else:
            pages_count = estimate_pages_from_text(texte)
        demande.pages_count = pages_count
        if pages_count <= 50:
            demande.payment_tier = 1
        elif pages_count <= 100:
            demande.payment_tier = 2
        elif pages_count <= 200:
            demande.payment_tier = 3
        elif pages_count <= 500:
            demande.payment_tier = 4
        elif pages_count <= 1000:
            demande.payment_tier = 5
        else:
            demande.payment_tier = 6

        demande.save()
        self.request.session["audio_request_id"] = demande.id
        return redirect("catalogue:conversion-audio-pay-required", demande_id=demande.id)


def _is_committee_member(user):
    return user.is_authenticated and user.groups.filter(name="ComiteLecture").exists()


@ensure_csrf_cookie
def committee_portal(request):
    """Portail du comité de lecture (inscription + connexion + accès évaluations)."""
    if request.user.is_authenticated:
        if _is_committee_member(request.user):
            submissions = SoumissionManuscrit.objects.all().order_by("-created_at")
            reviews_qs = ManuscriptReview.objects.filter(reviewer=request.user)
            reviews = {r.soumission_id: r for r in reviews_qs}

            # Filters
            q = (request.GET.get("q") or "").strip()
            genre = (request.GET.get("genre") or "").strip()
            nationalite = (request.GET.get("nationalite") or "").strip()
            pays = (request.GET.get("pays") or "").strip()
            decision = (request.GET.get("decision") or "").strip()
            statut = (request.GET.get("statut") or "").strip()

            if q:
                submissions = submissions.filter(
                    Q(titre_ouvrage__icontains=q)
                    | Q(nom_auteur__icontains=q)
                    | Q(nom_complet__icontains=q)
                )
            if genre:
                submissions = submissions.filter(genre_litteraire__iexact=genre)
            if nationalite:
                submissions = submissions.filter(nationalite__iexact=nationalite)
            if pays:
                submissions = submissions.filter(pays_residence__iexact=pays)

            items = [{"submission": submission, "review": reviews.get(submission.id)} for submission in submissions]

            if decision:
                items = [item for item in items if item["review"] and item["review"].decision == decision]
            if statut == "pending":
                items = [item for item in items if not item["review"]]
            elif statut == "done":
                items = [item for item in items if item["review"]]

            # Dropdown data
            genres = (
                SoumissionManuscrit.objects.exclude(genre_litteraire="")
                .values_list("genre_litteraire", flat=True)
                .distinct()
                .order_by("genre_litteraire")
            )
            nationalites = (
                SoumissionManuscrit.objects.exclude(nationalite="")
                .values_list("nationalite", flat=True)
                .distinct()
                .order_by("nationalite")
            )
            pays_list = (
                SoumissionManuscrit.objects.exclude(pays_residence="")
                .values_list("pays_residence", flat=True)
                .distinct()
                .order_by("pays_residence")
            )

            return render(
                request,
                "catalogue/committee_portal.html",
                {
                    "items": items,
                    "genres": genres,
                    "nationalites": nationalites,
                    "pays_list": pays_list,
                    "filters": {
                        "q": q,
                        "genre": genre,
                        "nationalite": nationalite,
                        "pays": pays,
                        "decision": decision,
                        "statut": statut,
                    },
                },
            )
        return render(request, "catalogue/committee_pending.html")

    login_form = AuthenticationForm(request, data=request.POST if request.POST.get("action") == "login" else None)
    login_form.fields["username"].widget.attrs.update({"placeholder": "Nom d’utilisateur ou E-mail"})
    login_form.fields["password"].widget.attrs.update({"placeholder": "Mot de passe"})

    if request.method == "POST" and request.POST.get("action") == "login" and login_form.is_valid():
        user = login_form.get_user()
        login(request, user)
        return redirect(request.path)

    return render(
        request,
        "catalogue/committee_auth.html",
        {"login_form": login_form},
    )


@ensure_csrf_cookie
def committee_signup(request):
    """Inscription comité de lecture (page dédiée)."""
    signup_form = CommitteeSignupForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and signup_form.is_valid():
        user = signup_form.save(commit=False)
        user.is_active = False
        user.set_password(signup_form.cleaned_data["password1"])
        user.save()
        group, _ = Group.objects.get_or_create(name="ComiteLecture")
        user.groups.add(group)
        CommitteeApplication.objects.create(
            user=user,
            cv=signup_form.cleaned_data["cv"],
            motivation=signup_form.cleaned_data["motivation"],
            confidentiality_ack=signup_form.cleaned_data["confidentiality_ack"],
            unpaid_ack=signup_form.cleaned_data["unpaid_ack"],
        )
        messages.success(
            request,
            _content_value(
                _get_site_content(),
                "committee_signup_success",
                "Votre demande a été envoyée. Un administrateur doit l’approuver.",
            ),
        )
        return redirect("catalogue:committee-portal")

    return render(
        request,
        "catalogue/committee_signup.html",
        {"signup_form": signup_form},
    )


def committee_submission_detail(request, pk):
    if not _is_committee_member(request.user):
        return redirect("catalogue:committee-portal")

    submission = get_object_or_404(SoumissionManuscrit, pk=pk)
    review, _ = ManuscriptReview.objects.get_or_create(
        soumission=submission,
        reviewer=request.user,
        defaults={"note": 0, "decision": "no"},
    )

    form = ManuscriptReviewForm(request.POST or None, instance=review)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            _content_value(
                _get_site_content(),
                "committee_review_saved",
                "\u00c9valuation enregistr\u00e9e.",
            ),
        )
        return redirect("catalogue:committee-submission", pk=submission.pk)

    return render(
        request,
        "catalogue/committee_submission_detail.html",
        {"submission": submission, "form": form, "review": review},
    )


def logout_view(request):
    """Logout compatible GET/POST to avoid 405 errors."""
    if request.method in ("GET", "POST"):
        logout(request)
        return redirect("catalogue:index")
    return redirect("catalogue:index")


class AudioConversionView(FormView):
    template_name = "catalogue/conversion-audio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context.get("site_content") and context["site_content"].conversion_meta_keywords:
            context["page_keywords"] = context["site_content"].conversion_meta_keywords
        return context
    form_class = AudioConversionForm
    success_url = reverse_lazy("catalogue:conversion-audio-synthetique")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = Page.objects.filter(slug="conversion-texte-audio", is_active=True).first()
        context["page"] = page
        context["page_blocks"] = (
            page.blocks.filter(est_actif=True)
            .prefetch_related("items")
            .order_by("ordre")
            if page
            else []
        )
        context["page_title"] = page.meta_title if page and page.meta_title else "Conversion de texte en audio - Editions Recr\u00e9ation"
        last_id = self.request.session.get("audio_request_id")
        if last_id:
            context["last_request"] = AudioConversionRequest.objects.filter(id=last_id).first()
            appearance = SiteAppearance.objects.first()
            if appearance and context["last_request"]:
                tier = context["last_request"].payment_tier or 1
                context["payment_url"] = {
                    1: appearance.audio_payment_url_1 or appearance.audio_payment_url,
                    2: appearance.audio_payment_url_2,
                    3: appearance.audio_payment_url_3,
                    4: appearance.audio_payment_url_4,
                    5: appearance.audio_payment_url_5,
                }.get(tier) or appearance.audio_payment_url
                context["payment_available"] = bool(context["payment_url"])
        return context

    def form_valid(self, form):
        texte = (form.cleaned_data.get("texte") or "").strip()
        fichier = form.cleaned_data.get("fichier")
        text_length = len(texte)


        demande = form.save(commit=False)
        demande.voice_type = "synthetic"
        appearance = SiteAppearance.objects.first()
        if appearance and not appearance.tts_use_normalization:
            demande.use_original_text = True
        if self.request.user.is_authenticated:
            demande.user = self.request.user
        demande.phrases_count = 0
        demande.paiement_requis = True if fichier else text_length > FREE_TEXT_LIMIT
        demande.statut = "awaiting_payment" if demande.paiement_requis else "processing"
        if fichier:
            pages_count = count_pages_for_file(
                fichier,
                language_hint=demande.langue,
                force_ocr=demande.force_ocr,
            )
        else:
            pages_count = estimate_pages_from_text(texte)
        demande.pages_count = pages_count
        if pages_count <= 50:
            demande.payment_tier = 1
        elif pages_count <= 100:
            demande.payment_tier = 2
        elif pages_count <= 200:
            demande.payment_tier = 3
        elif pages_count <= 500:
            demande.payment_tier = 4
        else:
            demande.payment_tier = 5
        demande.save()

        # Si paiement requis (fichier ou texte long), rediriger immédiatement vers le paiement
        if demande.paiement_requis:
            self.request.session["audio_request_id"] = demande.id
            return redirect("catalogue:conversion-audio-pay-required", demande_id=demande.id)

        # Extraire le texte depuis le fichier si nécessaire
        audio_text = texte
        if fichier:
            try:
                audio_text = extract_text_from_file(
                    fichier,
                    language_hint=demande.langue,
                    force_ocr=demande.force_ocr,
                ).strip()
                if audio_text:
                    demande.texte = audio_text
                    demande.save(update_fields=["texte", "updated_at"])
            except Exception as exc:
                demande.statut = "error"
                demande.async_error = str(exc)
                demande.save(update_fields=["statut", "async_error", "updated_at"])
                self.request.session["audio_request_id"] = demande.id
                return redirect(self.success_url)
            if not audio_text:
                demande.statut = "error"
                demande.async_error = "Aucun texte extrait."
                demande.save(update_fields=["statut", "async_error", "updated_at"])
                self.request.session["audio_request_id"] = demande.id
                return redirect(self.success_url)

        if audio_text:
            # Détection langue si auto
            if demande.langue == "auto":
                detected_lang = detect_tts_language(audio_text, selected="auto")
                if detected_lang and detected_lang != demande.langue:
                    demande.langue = detected_lang
                    demande.save(update_fields=["langue", "updated_at"])

            appearance = appearance or SiteAppearance.objects.first()
            normalized_text = normalize_tts_text(
                audio_text,
                appearance=appearance,
                use_original=demande.use_original_text,
            )
            if normalized_text and normalized_text != audio_text:
                demande.texte_normalise = normalized_text
                demande.save(update_fields=["texte_normalise", "updated_at"])
            else:
                normalized_text = audio_text

            try:
                from gtts import gTTS
            except Exception:
                self.request.session["audio_request_id"] = demande.id
                return redirect(self.success_url)

            def _generate_audio(demande_id, text, langue, voix):
                close_old_connections()
                try:
                    import uuid
                    obj = AudioConversionRequest.objects.get(pk=demande_id)
                    slow = True if voix == "slow" else False
                    tts = gTTS(text, lang=langue, slow=slow)
                    audio_bytes = ContentFile(b"")
                    filename = f"conversion-{uuid.uuid4().hex}.mp3"
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    obj.audio.save(filename, audio_bytes, save=False)
                    obj.save(update_fields=["audio", "updated_at"])
                except Exception:
                    obj = AudioConversionRequest.objects.filter(pk=demande_id).first()
                    if obj:
                        obj.statut = "error"
                        obj.save(update_fields=["statut", "updated_at"])

            if not demande.paiement_requis:
                try:
                    _generate_audio(demande.id, normalized_text, demande.langue, demande.voix)
                except Exception:
                    demande.statut = "error"
                    demande.save(update_fields=["statut", "updated_at"])
                    self.request.session["audio_request_id"] = demande.id
                    messages.error(
                        self.request,
                        _content_value(
                            _get_site_content(),
                            "audio_message_failed",
                            "La g\u00e9n\u00e9ration de l\u2019audio a \u00e9chou\u00e9. Veuillez r\u00e9essayer.",
                        ),
                    )
                    return redirect(self.success_url)

                demande.refresh_from_db()
                if demande.audio:
                    demande.statut = "free_generated"
                    demande.save(update_fields=["statut", "updated_at"])
                    messages.success(
                        self.request,
                        _content_value(
                            _get_site_content(),
                            "audio_message_success",
                            "Votre audio est pr\u00eat. Vous pouvez l'\u00e9couter en cliquant sur play. Vous pouvez aussi le t\u00e9l\u00e9charger gratuitement.",
                        ),
                    )
                else:
                    demande.statut = "error"
                    demande.save(update_fields=["statut", "updated_at"])
                    messages.error(
                        self.request,
                        _content_value(
                            _get_site_content(),
                            "audio_message_not_ready",
                            "La g\u00e9n\u00e9ration de l\u2019audio n\u2019a pas abouti. Veuillez r\u00e9essayer.",
                        ),
                    )

        self.request.session["audio_request_id"] = demande.id

        return redirect(self.success_url)


def conversion_payment_redirect(request, demande_id):
    demande = get_object_or_404(AudioConversionRequest, id=demande_id)
    if demande.paiement_initie_at is None:
        demande.paiement_initie_at = timezone.now()
        demande.save(update_fields=["paiement_initie_at", "updated_at"])
        appearance = SiteAppearance.objects.first()
        if appearance and appearance.site_email:
            send_mail(
                "Paiement initié - Conversion audio",
                f"Une demande de conversion audio a initié le paiement.\n"
                f"ID: {demande.id}\nEmail: {demande.email}\n",
                appearance.site_email,
                [appearance.site_email],
                fail_silently=True,
            )
    appearance = SiteAppearance.objects.first()
    tier = demande.payment_tier or 1
    payment_url = ""
    if appearance:
        if demande.voice_type == "human":
            payment_url = {
                1: appearance.audio_human_payment_url_1 or appearance.audio_human_payment_url,
                2: appearance.audio_human_payment_url_2,
                3: appearance.audio_human_payment_url_3,
                4: appearance.audio_human_payment_url_4,
                5: appearance.audio_human_payment_url_5,
                6: appearance.audio_human_payment_url_6,
            }.get(tier) or appearance.audio_human_payment_url
        else:
            payment_url = {
                1: appearance.audio_payment_url_1 or appearance.audio_payment_url,
                2: appearance.audio_payment_url_2,
                3: appearance.audio_payment_url_3,
                4: appearance.audio_payment_url_4,
                5: appearance.audio_payment_url_5,
            }.get(tier) or appearance.audio_payment_url

    if request.GET.get("ajax") == "1" or request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "ok": True,
                "payment_url": payment_url,
                "has_widget": False,
            }
        )

    if payment_url:
        return redirect(payment_url)
    return redirect("catalogue:conversion-audio")


def conversion_payment_required(request, demande_id):
    """Page intermédiaire : paiement requis avant génération."""
    demande = get_object_or_404(AudioConversionRequest, id=demande_id)
    appearance = SiteAppearance.objects.first()
    tier = demande.payment_tier or 1
    payment_url = ""
    if appearance:
        if demande.voice_type == "human":
            payment_url = {
                1: appearance.audio_human_payment_url_1 or appearance.audio_human_payment_url,
                2: appearance.audio_human_payment_url_2,
                3: appearance.audio_human_payment_url_3,
                4: appearance.audio_human_payment_url_4,
                5: appearance.audio_human_payment_url_5,
                6: appearance.audio_human_payment_url_6,
            }.get(tier) or appearance.audio_human_payment_url
        else:
            payment_url = {
                1: appearance.audio_payment_url_1 or appearance.audio_payment_url,
                2: appearance.audio_payment_url_2,
                3: appearance.audio_payment_url_3,
                4: appearance.audio_payment_url_4,
                5: appearance.audio_payment_url_5,
            }.get(tier) or appearance.audio_payment_url

    context = {
        "demande": demande,
        "payment_url": payment_url,
        "page_title": "Paiement requis - Editions Récréation",
    }
    return render(request, "catalogue/conversion-audio-payment-required.html", context)


def conversion_payment_already_paid(request, demande_id):
    """Marque une demande comme paiement à vérifier (sans générer)."""
    demande = get_object_or_404(AudioConversionRequest, id=demande_id)
    if demande.statut != "paid":
        demande.statut = "payment_pending"
        demande.save(update_fields=["statut", "updated_at"])
    appearance = SiteAppearance.objects.first()
    if appearance and appearance.site_email:
        try:
            send_mail(
                "Paiement à vérifier - Conversion audio",
                f"Demande ID: {demande.id}\n"
                f"Email: {demande.email}\n"
                f"Type: {'Voix humaine' if demande.voice_type == 'human' else 'Voix synthétique'}\n"
                f"Pages: {demande.pages_count}\n",
                appearance.site_email,
                [appearance.site_email],
                fail_silently=True,
            )
        except Exception:
            pass
    messages.info(
        request,
        _content_value(
            _get_site_content(),
            "audio_payment_pending_message",
            "Merci. Nous allons v\u00e9rifier votre paiement et vous contacter tr\u00e8s rapidement par e-mail.",
        ),
    )
    return redirect("catalogue:conversion-audio")


@csrf_exempt
def conversion_payment_callback(request):
    """Callback paiement: marque la demande comme payée et génère l'audio."""
    token = request.POST.get("token") or request.GET.get("token")
    expected = getattr(settings, "PAYMENT_CALLBACK_TOKEN", "")
    if expected and token != expected:
        return JsonResponse({"ok": False, "error": "Token invalide."}, status=403)

    demande_id = request.POST.get("demande_id") or request.GET.get("demande_id") or request.POST.get("id") or request.GET.get("id")
    if not demande_id:
        return JsonResponse({"ok": False, "error": "ID manquant."}, status=400)

    demande = AudioConversionRequest.objects.filter(id=demande_id).first()
    if not demande:
        return JsonResponse({"ok": False, "error": "Demande introuvable."}, status=404)

    demande.statut = "paid"
    if demande.paiement_initie_at is None:
        demande.paiement_initie_at = timezone.now()
    demande.save(update_fields=["statut", "paiement_initie_at", "updated_at"])

    if demande.audio:
        return JsonResponse({"ok": True, "status": "already_generated"})

    # Génération audio après paiement
    try:
        text = demande.texte or ""
        if demande.fichier and not text.strip():
            text = extract_text_from_file(
                demande.fichier,
                language_hint=demande.langue,
                force_ocr=demande.force_ocr,
            )
            if text and not demande.texte:
                demande.texte = text
                demande.save(update_fields=["texte", "updated_at"])

        if not text.strip():
            demande.statut = "error"
            demande.async_error = "Texte vide après extraction."
            demande.save(update_fields=["statut", "async_error", "updated_at"])
            return JsonResponse({"ok": False, "error": "Texte vide."}, status=400)

        if demande.langue == "auto":
            detected_lang = detect_tts_language(text, selected="auto")
            if detected_lang and detected_lang != demande.langue:
                demande.langue = detected_lang
                demande.save(update_fields=["langue", "updated_at"])

        appearance = SiteAppearance.objects.first()
        normalized_text = normalize_tts_text(
            text,
            appearance=appearance,
            use_original=demande.use_original_text,
        )
        if normalized_text and normalized_text != text:
            demande.texte_normalise = normalized_text
            demande.save(update_fields=["texte_normalise", "updated_at"])

        from gtts import gTTS
        import uuid
        audio_bytes = ContentFile(b"")
        tts = gTTS(normalized_text or text, lang=demande.langue, slow=False)
        filename = f"conversion-{uuid.uuid4().hex}.mp3"
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        demande.audio.save(filename, audio_bytes, save=False)
        demande.statut = "delivered"
        demande.save(update_fields=["audio", "statut", "updated_at"])
        return JsonResponse({"ok": True, "status": "generated"})
    except Exception as exc:
        demande.statut = "error"
        demande.async_error = str(exc)
        demande.save(update_fields=["statut", "async_error", "updated_at"])
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)


class SignupView(FormView):
    template_name = "registration/signup.html"
    form_class = StyledSignupForm
    success_url = reverse_lazy("catalogue:conversion-audio")

    def form_valid(self, form):
        form.instance.is_active = False
        user = form.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = self.request.build_absolute_uri(
            reverse_lazy("catalogue:activate", kwargs={"uidb64": uid, "token": token})
        )
        appearance = SiteAppearance.objects.first()
        from_email = appearance.site_email if appearance and appearance.site_email else None
        send_mail(
            "Confirmez votre compte",
            f"Bonjour {user.first_name},\n\nMerci de confirmer votre compte en cliquant sur ce lien :\n{activation_link}\n\nEditions Recréation",
            from_email,
            [user.email],
            fail_silently=True,
        )

        messages.success(
            self.request,
            _content_value(
                _get_site_content(),
                "account_signup_success",
                "Compte cr\u00e9\u00e9. Un email de confirmation vous a \u00e9t\u00e9 envoy\u00e9. Activez votre compte pour continuer.",
            ),
        )
        return super().form_valid(form)


def activate_account(request, uidb64, token):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        login(request, user)
        messages.success(
            request,
            _content_value(
                _get_site_content(),
                "account_activation_success",
                "Votre compte est activ\u00e9. Vous pouvez utiliser le service.",
            ),
        )
        return redirect("catalogue:conversion-audio")
    messages.error(
        request,
        _content_value(
            _get_site_content(),
            "account_activation_invalid",
            "Lien d\u2019activation invalide ou expir\u00e9.",
        ),
    )
    return redirect("catalogue:login")


class LoginView(DjangoLoginView):
    authentication_form = StyledLoginForm
    template_name = "registration/login.html"

    def form_valid(self, form):
        username_or_email = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=username_or_email, password=password)
        if user is None:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
            except User.DoesNotExist:
                user_obj = None
            if user_obj:
                user = authenticate(self.request, username=user_obj.username, password=password)

        if user is None:
            messages.error(
                self.request,
                _content_value(
                    _get_site_content(),
                    "account_login_invalid",
                    "Identifiants invalides.",
                ),
            )
            return self.form_invalid(form)
        login(self.request, user)
        return super(DjangoLoginView, self).form_valid(form)


class PasswordResetView(DjangoPasswordResetView):
    template_name = "registration/password_reset_form.html"

    def get_from_email(self):
        appearance = SiteAppearance.objects.first()
        return appearance.site_email if appearance and appearance.site_email else None

    def form_valid(self, form):
        form.from_email = self.get_from_email()
        return super().form_valid(form)


# -------------------------------------------------------------------------------
# FONCTIONS DEPRECATED (compatibilite URLs)
# -------------------------------------------------------------------------------

def inscription_newsletter(request):
    """[DEPRECATED] Utiliser IndexView.post() a la place."""

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        content = _get_site_content()
        if email:
            inscription, created = InscriptionNewsletter.objects.get_or_create(
                email=email,
                defaults={"est_actif": True},
            )
            if created:
                messages.success(
                    request,
                    _content_value(
                        content,
                        "newsletter_message_success",
                        "Merci ! Vous \u00eates inscrit \u00e0 notre newsletter.",
                    ),
                )
            else:
                if not inscription.est_actif:
                    inscription.est_actif = True
                    inscription.save()
                    messages.success(
                        request,
                        _content_value(
                            content,
                            "newsletter_message_reactivated",
                            "Votre inscription a \u00e9t\u00e9 r\u00e9activ\u00e9e.",
                        ),
                    )
                else:
                    messages.info(
                        request,
                        _content_value(
                            content,
                            "newsletter_message_already",
                            "Vous \u00eates d\u00e9j\u00e0 inscrit.",
                        ),
                    )
        else:
            messages.error(
                request,
                _content_value(
                    content,
                    "newsletter_message_invalid",
                    "Veuillez saisir une adresse email valide.",
                ),
            )

    return redirect(request.META.get("HTTP_REFERER", "catalogue:index"))


def contact_submit(request):
    """[DEPRECATED] Utiliser ContactView a la place."""

    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        email = request.POST.get("email", "").strip()
        telephone = request.POST.get("telephone", "").strip()
        sujet = request.POST.get("sujet", "").strip()
        message_text = request.POST.get("message", "").strip()

        if nom and email and sujet and message_text:
            MessageContact.objects.create(
                nom=nom,
                email=email,
                telephone=telephone,
                sujet=sujet,
                message=message_text,
            )
            messages.success(
                request,
                _content_value(
                    _get_site_content(),
                    "contact_message_success",
                    "Votre message a \u00e9t\u00e9 envoy\u00e9 avec succ\u00e8s.",
                ),
            )
            return redirect("catalogue:contact")
        messages.error(
            request,
            _content_value(
                _get_site_content(),
                "contact_message_missing",
                "Veuillez remplir tous les champs obligatoires.",
            ),
        )

    return redirect("catalogue:contact")


# -------------------------------------------------------------------------------
# API JSON
# -------------------------------------------------------------------------------

def livres_json(request):
    """API JSON livres."""

    livres = Livre.objects.filter(est_publie=True).prefetch_related("auteurs").all()
    data = {
        "livres": [
            {
                "id": livre.id,
                "titre": livre.titre,
                "auteurs": [{"id": a.id, "nom": a.nom} for a in livre.auteurs.all()],
                "categorie": livre.categorie,
                "collection": livre.collection.nom if livre.collection else "",
                "collection_slug": livre.collection.slug if livre.collection else "",
                "parution": livre.parution.isoformat(),
                "prix": livre.prix,
                "isbn": livre.isbn,
                "image": livre.image_par_defaut().url if livre.image_par_defaut() else "",
                "resume": livre.resume,
                "slug": livre.slug,
                "langue": livre.langue_publication,
                "versions": livre.versions_disponibles(),
            }
            for livre in livres
        ]
    }
    return JsonResponse(data)


def auteurs_json(request):
    """API JSON auteurs."""

    auteurs = Auteur.objects.all()
    data = {
        "auteurs": [
            {
                "id": auteur.id,
                "nom": auteur.nom,
                "specialite": auteur.specialite,
                "photo": auteur.photo.url if auteur.photo else "",
                "biographie": auteur.biographie,
                "slug": auteur.slug,
            }
            for auteur in auteurs
        ]
    }
    return JsonResponse(data)


def robots_txt(request):
    base_url = f"{request.scheme}://{request.get_host()}"
    content = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {base_url}/sitemap.xml",
        ]
    )
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    base_url = f"{request.scheme}://{request.get_host()}"

    def _url(path):
        return f"{base_url}{path}"

    static_paths = [
        "/",
        "/catalogue/",
        "/collections/",
        "/auteurs/",
        "/actualites/",
        "/a-propos/",
        "/contact/",
        "/nos-contrats/",
        "/conversion-texte-audio/",
        "/conversion-texte-audio/synthetique/",
        "/conversion-texte-audio/humaine/",
        "/lecture-evaluation-des-soumissions-de-manuscrit-ou-tapuscrits/",
    ]

    entries = []
    for path in static_paths:
        entries.append({"loc": _url(path)})

    for page in Page.objects.filter(is_active=True):
        entries.append({"loc": _url(f"/page/{page.slug}/"), "lastmod": page.updated_at})

    for actualite in Actualite.objects.filter(est_publie=True):
        entries.append({"loc": _url(f"/actualite/{actualite.slug}/"), "lastmod": actualite.updated_at})

    for auteur in Auteur.objects.all():
        entries.append({"loc": _url(f"/auteur/{auteur.slug}/"), "lastmod": auteur.updated_at})

    for collection in Collection.objects.all():
        entries.append({"loc": _url(f"/collection/{collection.slug}/"), "lastmod": collection.updated_at})

    for livre in Livre.objects.filter(est_publie=True):
        entries.append({"loc": _url(f"/livre/{livre.slug}/"), "lastmod": livre.updated_at})

    for membre in Membre.objects.filter(est_actif=True):
        entries.append({"loc": _url(f"/equipe/{membre.pk}/"), "lastmod": membre.updated_at})

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for entry in entries:
        lines.append("  <url>")
        lines.append(f"    <loc>{entry['loc']}</loc>")
        lastmod = entry.get("lastmod")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod.date().isoformat()}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return HttpResponse("\n".join(lines), content_type="application/xml")


def livre_detail_json(request, livre_id):
    """API JSON detail livre."""

    livre = get_object_or_404(Livre, id=livre_id, est_publie=True)
    data = {
        "id": livre.id,
        "titre": livre.titre,
        "auteurs": [{"id": a.id, "nom": a.nom} for a in livre.auteurs.all()],
        "categorie": livre.get_categorie_display(),
        "collection": livre.collection.nom if livre.collection else "",
        "collection_slug": livre.collection.slug if livre.collection else "",
        "resume": livre.resume,
        "isbn": livre.isbn,
        "prix": livre.prix,
        "parution": livre.parution.strftime("%d/%m/%Y"),
        "image": livre.image_par_defaut().url if livre.image_par_defaut() else "",
        "langue": livre.langue_publication,
        "versions": livre.versions_disponibles(),
        "liens": {
            "papier": {
                "chariow": livre.lien_chariow,
                "amazon": livre.lien_amazon,
                "whatsapp": livre.lien_whatsapp,
            },
            "numerique": {
                "chariow": livre.lien_chariow_numerique,
                "amazon": livre.lien_amazon_numerique,
                "whatsapp": livre.lien_whatsapp_numerique,
            },
            "audio": {
                "chariow": livre.lien_chariow_audio,
                "amazon": livre.lien_amazon_audio,
                "whatsapp": livre.lien_whatsapp_audio,
            },
        },
    }
    return JsonResponse(data)
