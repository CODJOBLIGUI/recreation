"""
FICHIER : apps/catalogue/views.py
"""

from django.contrib import messages
from django.db.models import Q
from django.db import close_old_connections
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.utils import timezone
from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.safestring import mark_safe
from django.core.mail import send_mail
from django.core.cache import cache
from django.contrib.auth.views import LoginView as DjangoLoginView, PasswordResetView as DjangoPasswordResetView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date
import unicodedata

from .forms import ContactForm, NewsletterForm, SoumissionManuscritForm, AudioConversionForm, StyledSignupForm, StyledLoginForm
from .utils.audio_conversion import (
    estimate_pages_from_text,
    count_pages_for_file,
    detect_language,
    extract_text_from_file,
    generate_tts_mp3,
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
)
from apps.core.models import SiteAppearance


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
            context["page_title"] = "Editions Recr\u00e9ation | Maison d'\u00e9dition - Recreation book publisher"
        if "page_description" not in context:
            context["page_description"] = (
                "Editions Recr\u00e9ation (Recreation) - maison d'\u00e9dition / book publisher. "
                "Livres papier, num\u00e9riques et audio."
            )
        last_id = self.request.session.pop("audio_request_id", None)
        if last_id:
            context["last_request"] = AudioConversionRequest.objects.filter(id=last_id).first()
        return context

    def post(self, request, *args, **kwargs):
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            inscription, created = InscriptionNewsletter.objects.get_or_create(
                email=email,
                defaults={"est_actif": True},
            )
            if created:
                messages.success(request, "Merci ! Vous \u00eates inscrit \u00e0 notre newsletter.")
            else:
                if not inscription.est_actif:
                    inscription.est_actif = True
                    inscription.save(update_fields=["est_actif", "updated_at"])
                    messages.success(request, "Votre inscription a \u00e9t\u00e9 r\u00e9activ\u00e9e.")
                else:
                    messages.info(request, "Vous \u00eates d\u00e9j\u00e0 inscrit.")
        else:
            messages.error(request, "Une erreur s'est produite. Veuillez v\u00e9rifier votre email.")

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
        context["collections_list"] = Collection.objects.filter(est_active=True).order_by("nom")
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
        if isinstance(queryset, list):
            return [livre for livre in queryset if livre.version_numerique]
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
        if isinstance(queryset, list):
            return [livre for livre in queryset if livre.version_audio]
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
        if isinstance(queryset, list):
            return [livre for livre in queryset if livre.version_papier]
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
        return context

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Votre message a \u00e9t\u00e9 envoy\u00e9 avec succ\u00e8s ! Nous vous r\u00e9pondrons dans les plus brefs d\u00e9lais.",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Une erreur s'est produite. Veuillez v\u00e9rifier les informations saisies.",
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
        context["annees_experience"] = max(1, date.today().year - 2023)
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
        return context


# -------------------------------------------------------------------------------
# COLLECTIONS
# -------------------------------------------------------------------------------

class CollectionsListView(ListView):
    """Vue liste des collections."""

    model = Collection
    template_name = "catalogue/collections.html"
    context_object_name = "collections"

    def get_queryset(self):
        return Collection.objects.filter(est_active=True).order_by("nom")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Collections - Editions Recréation"
        context["page_description"] = "Découvrez toutes nos collections."
        return context


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
        return context


class SoumissionManuscritView(FormView):
    """Vue page soumission de manuscrit."""

    template_name = "catalogue/soumission-manuscrit.html"
    form_class = SoumissionManuscritForm
    success_url = reverse_lazy("catalogue:soumission-manuscrit")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = Page.objects.filter(slug="soumission-manuscrit", is_active=True).first()
        return context

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Merci ! Votre manuscrit a \u00e9t\u00e9 soumis avec succ\u00e8s. Nous vous contacterons rapidement.",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Une erreur s'est produite. Veuillez v\u00e9rifier les informations saisies.",
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
        return context




class SearchView(TemplateView):
    """Vue page recherche globale."""

    template_name = "catalogue/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = Page.objects.filter(slug="recherche", is_active=True).first()
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
        annee = self.request.GET.get("annee", "")
        mois = self.request.GET.get("mois", "")
        if annee:
            qs = qs.filter(date_publication__year=annee)
        if mois:
            qs = qs.filter(date_publication__month=mois)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Actualités - Editions Recréation"
        context["annee_actuelle"] = self.request.GET.get("annee", "")
        context["mois_actuel"] = self.request.GET.get("mois", "")
        context["annees_actualites"] = [
            d.year
            for d in Actualite.objects.filter(est_publie=True).dates(
                "date_publication", "year", order="DESC"
            )
        ]
        context["mois_actualites"] = [
            {"value": 1, "label": "Janvier"},
            {"value": 2, "label": "Février"},
            {"value": 3, "label": "Mars"},
            {"value": 4, "label": "Avril"},
            {"value": 5, "label": "Mai"},
            {"value": 6, "label": "Juin"},
            {"value": 7, "label": "Juillet"},
            {"value": 8, "label": "Août"},
            {"value": 9, "label": "Septembre"},
            {"value": 10, "label": "Octobre"},
            {"value": 11, "label": "Novembre"},
            {"value": 12, "label": "Décembre"}
        ]
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
FREE_CONVERSION_LIMIT = 3
FREE_LIMIT_MESSAGE = (
    "Vous venez de faire trois essais gratuits. Inscrivez-vous ou connectez-vous "
    "pour continuer d'utiliser ce service gratuitement tant que votre texte ne "
    "dépasse pas la longueur autorisée pour ce mode."
)
FREE_IP_LIMIT = 10
FREE_IP_WINDOW_SECONDS = 7 * 60 * 60


def _get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or "unknown"


def _get_free_ip_state(ip):
    key = f"free_audio_ip:{ip}"
    data = cache.get(key)
    now = timezone.now().timestamp()
    if not data or data.get("reset_at", 0) <= now:
        data = {"count": 0, "reset_at": now + FREE_IP_WINDOW_SECONDS}
        cache.set(key, data, timeout=FREE_IP_WINDOW_SECONDS)
    return data, key


def _is_free_ip_blocked(request):
    ip = _get_client_ip(request)
    data, _ = _get_free_ip_state(ip)
    remaining = max(0, int(data["reset_at"] - timezone.now().timestamp()))
    return data["count"] >= FREE_IP_LIMIT, remaining


def _record_free_ip_success(request):
    ip = _get_client_ip(request)
    data, key = _get_free_ip_state(ip)
    data["count"] = min(FREE_IP_LIMIT, data.get("count", 0) + 1)
    cache.set(key, data, timeout=FREE_IP_WINDOW_SECONDS)


class AudioConversionView(FormView):
    template_name = "catalogue/conversion-audio.html"
    form_class = AudioConversionForm
    success_url = reverse_lazy("catalogue:conversion-audio-synthetique")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = (
            Page.objects.filter(slug="conversion-texte-audio-synthetique", is_active=True).first()
            or Page.objects.filter(slug="conversion-texte-audio", is_active=True).first()
        )
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
        if not last_id:
            req_id = self.request.GET.get("req")
            if req_id and req_id.isdigit():
                last_id = int(req_id)
                self.request.session["audio_request_id"] = last_id
        if last_id:
            context["last_request"] = AudioConversionRequest.objects.filter(id=last_id).first()
            appearance = SiteAppearance.objects.first()
            if appearance and context["last_request"]:
                tier = context["last_request"].payment_tier or 1
                if context["last_request"].lecture_humaine:
                    context["payment_url"] = {
                        1: getattr(appearance, "audio_human_payment_url_0", "") or appearance.audio_human_payment_url,
                        2: getattr(appearance, "audio_human_payment_url_1", "") or appearance.audio_human_payment_url,
                        3: getattr(appearance, "audio_human_payment_url_2", ""),
                        4: getattr(appearance, "audio_human_payment_url_3", ""),
                        5: getattr(appearance, "audio_human_payment_url_4", ""),
                        6: getattr(appearance, "audio_human_payment_url_5", ""),
                    }.get(tier) or appearance.audio_human_payment_url
                else:
                    context["payment_url"] = {
                        1: getattr(appearance, "audio_payment_url_0", "") or appearance.audio_payment_url,
                        2: getattr(appearance, "audio_payment_url_1", "") or appearance.audio_payment_url,
                        3: getattr(appearance, "audio_payment_url_2", ""),
                        4: getattr(appearance, "audio_payment_url_3", ""),
                        5: getattr(appearance, "audio_payment_url_4", ""),
                        6: getattr(appearance, "audio_payment_url_5", ""),
                    }.get(tier) or appearance.audio_payment_url
                context["payment_available"] = bool(context["payment_url"])
        context["free_limit_blocked"] = getattr(self, "free_limit_blocked", False)
        context["free_limit_remaining"] = getattr(self, "free_limit_remaining", 0)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            success_count = int(request.session.get("audio_success_count", 0) or 0)
            if success_count >= FREE_CONVERSION_LIMIT:
                messages.info(request, FREE_LIMIT_MESSAGE)
                return redirect("catalogue:login")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        texte = (form.cleaned_data.get("texte") or "").strip()
        fichier = form.cleaned_data.get("fichier")
        text_length = len(texte)
        human_reading = (self.request.POST.get("human_reading") or "") == "1"

        if not human_reading and form.cleaned_data.get("langue") == "fon":
            message = (
                "La synthèse vocale en fon n’est pas disponible pour le moment. "
                "Choisissez ‘Lecture par un humain’ "
                f"(<a href=\"{reverse_lazy('catalogue:conversion-audio-humain')}\">ouvrir l’interface</a>)."
            )
            form.add_error(
                "langue",
                "La synthèse vocale en fon n’est pas disponible. Choisissez ‘Lecture par un humain’.",
            )
            messages.error(self.request, mark_safe(message))
            return self.form_invalid(form)


        demande = form.save(commit=False)
        if self.request.user.is_authenticated:
            demande.user = self.request.user
        demande.phrases_count = 0
        demande.lecture_humaine = human_reading
        demande.voix_humaine = form.cleaned_data.get("voix_humaine") or ""
        demande.paiement_requis = True if human_reading else (True if fichier else text_length > FREE_TEXT_LIMIT)
        demande.statut = "awaiting_payment" if demande.paiement_requis else "processing"
        demande.async_status = "queued"
        demande.async_progress = 0
        if not demande.paiement_requis and not human_reading:
            blocked, remaining = _is_free_ip_blocked(self.request)
            if blocked:
                self.free_limit_blocked = True
                self.free_limit_remaining = remaining
                messages.error(
                    self.request,
                    "Vous avez atteint la limite de conversion gratuite quotidienne.",
                )
                return self.form_invalid(form)
        if fichier:
            pages_count = count_pages_for_file(fichier)
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

        def _set_async(obj, status, progress, error=""):
            obj.async_status = status
            obj.async_progress = progress
            if error:
                obj.async_error = error
            obj.save(update_fields=["async_status", "async_progress", "async_error", "updated_at"])

        # Extraire le texte depuis le fichier si nécessaire
        audio_text = texte
        if fichier:
            try:
                _set_async(demande, "started", 20)
                audio_text = extract_text_from_file(fichier).strip()
                if audio_text:
                    demande.texte = audio_text
            except Exception as exc:
                demande.statut = "error"
                demande.async_error = str(exc)
                demande.save(update_fields=["statut", "async_error", "updated_at"])
                self.request.session["audio_request_id"] = demande.id
                return redirect(self.success_url)

        detected = detect_language(audio_text)
        if detected in {"fr", "en", "es", "de"} and detected != demande.langue:
            labels = {"fr": "français", "en": "anglais", "es": "espagnol", "de": "allemand"}
            messages.warning(
                self.request,
                f"Attention : votre texte semble être en {labels.get(detected, detected)}. "
                f"Vous avez choisi la langue {labels.get(demande.langue, demande.langue)}.",
            )

        if audio_text and not human_reading:
            try:
                from gtts import gTTS
            except Exception:
                messages.error(self.request, "Conversion indisponible pour le moment. Veuillez réessayer plus tard.")
                self.request.session["audio_request_id"] = demande.id
                return redirect(self.success_url)

            def _generate_audio(demande_id, text, langue, voix, is_free):
                close_old_connections()
                import uuid
                obj = AudioConversionRequest.objects.get(pk=demande_id)
                _set_async(obj, "started", 60)
                slow = True if voix == "slow" else False
                audio_stream = generate_tts_mp3(text, lang=langue, slow=slow, chunk_size=1000)
                audio_bytes = ContentFile(audio_stream.getvalue())
                filename = f"conversion-{uuid.uuid4().hex}.mp3"
                obj.audio.save(filename, audio_bytes, save=True)
                if is_free:
                    obj.statut = "free_generated"
                    obj.save(update_fields=["statut", "updated_at"])
                _set_async(obj, "finished", 100)

            if demande.paiement_requis:
                import threading
                def _run_thread():
                    try:
                        _set_async(demande, "started", 40)
                        _generate_audio(demande.id, audio_text, demande.langue, demande.voix, False)
                    except Exception as exc:
                        obj = AudioConversionRequest.objects.filter(pk=demande.id).first()
                        if obj:
                            obj.statut = "error"
                            obj.async_error = str(exc)
                            obj.save(update_fields=["statut", "async_error", "updated_at"])

                threading.Thread(target=_run_thread, daemon=True).start()
            else:
                import threading
                def _run_free_thread():
                    try:
                        _set_async(demande, "started", 40)
                        _generate_audio(demande.id, audio_text, demande.langue, demande.voix, True)
                    except Exception as exc:
                        obj = AudioConversionRequest.objects.filter(pk=demande.id).first()
                        if obj:
                            obj.statut = "error"
                            obj.async_error = str(exc)
                            _set_async(obj, "failed", 100, str(exc))
                            obj.save(update_fields=["statut", "async_error", "updated_at"])

                threading.Thread(target=_run_free_thread, daemon=True).start()

        self.request.session["audio_request_id"] = demande.id

        if demande.paiement_requis:
            if human_reading:
                messages.info(self.request, "Votre demande de lecture par un humain est enregistrée. Procédez au paiement pour lancer la prise en charge.")
            else:
                messages.info(self.request, "Texte trop long en mode gratuit ou fichier téléversé. Veuillez payer pour recevoir l’audio.")
            # Rester sur la page de conversion pour afficher le bouton "Payer maintenant"
            return redirect(f"{self.success_url}?req={demande.id}")

        messages.info(self.request, "Conversion en cours. La page se mettra à jour automatiquement.")
        return redirect(self.success_url)

    def form_invalid(self, form):
        # Surface first error clearly for users (especially for human-reading)
        if form.non_field_errors():
            messages.error(self.request, form.non_field_errors()[0])
        else:
            # Pick the first field error with label
            for field_name, field_errors in form.errors.items():
                if field_errors:
                    label = form.fields.get(field_name).label if field_name in form.fields else field_name
                    messages.error(self.request, f"{label} : {field_errors[0]}")
                    break
        return super().form_invalid(form)


class AudioConversionHumanView(AudioConversionView):
    template_name = "catalogue/conversion-audio-humain.html"
    success_url = reverse_lazy("catalogue:conversion-audio-humain")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Hide synthetic voice field for human reading but keep it to satisfy ModelForm.
        if "voix" in form.fields:
            form.fields["voix"].required = False
            form.fields["voix"].widget = forms.HiddenInput()
            form.fields["voix"].initial = "standard"
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = (
            Page.objects.filter(slug="conversion-texte-audio-humain", is_active=True).first()
            or Page.objects.filter(slug="conversion-texte-audio", is_active=True).first()
        )
        context["page"] = page
        context["human_reading_page"] = True
        form = context.get("form")
        if form and "texte" in form.fields:
            form.fields["texte"].widget.attrs["placeholder"] = "Collez votre texte ici."
        return context


class AudioConversionChoiceView(TemplateView):
    template_name = "catalogue/conversion-audio-choice.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = (
            Page.objects.filter(slug="conversion-texte-audio-choix", is_active=True).first()
            or Page.objects.filter(slug="conversion-texte-audio", is_active=True).first()
        )
        context["page"] = page
        context["page_title"] = (
            page.meta_title if page and page.meta_title else "Conversion de texte en audio - Editions Recréation"
        )
        return context

def conversion_status(request, demande_id):
    demande = get_object_or_404(AudioConversionRequest, id=demande_id)
    if (
        not request.user.is_authenticated
        and demande.audio
        and not demande.paiement_requis
        and demande.statut == "free_generated"
    ):
        counted = request.session.get("audio_counted_ids", [])
        if demande.id not in counted:
            success_count = int(request.session.get("audio_success_count", 0) or 0)
            request.session["audio_success_count"] = success_count + 1
            counted.append(demande.id)
            request.session["audio_counted_ids"] = counted
        _record_free_ip_success(request)
    return JsonResponse(
        {
            "id": demande.id,
            "status": demande.statut,
            "async_status": demande.async_status,
            "progress": demande.async_progress or 0,
            "audio_url": demande.audio.url if demande.audio else "",
            "payment_required": bool(demande.paiement_requis),
        }
    )


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
        if demande.lecture_humaine:
            payment_url = {
                1: getattr(appearance, "audio_human_payment_url_0", "") or appearance.audio_human_payment_url,
                2: getattr(appearance, "audio_human_payment_url_1", "") or appearance.audio_human_payment_url,
                3: getattr(appearance, "audio_human_payment_url_2", ""),
                4: getattr(appearance, "audio_human_payment_url_3", ""),
                5: getattr(appearance, "audio_human_payment_url_4", ""),
                6: getattr(appearance, "audio_human_payment_url_5", ""),
            }.get(tier) or appearance.audio_human_payment_url
        else:
            payment_url = {
                1: getattr(appearance, "audio_payment_url_0", "") or appearance.audio_payment_url,
                2: getattr(appearance, "audio_payment_url_1", "") or appearance.audio_payment_url,
                3: getattr(appearance, "audio_payment_url_2", ""),
                4: getattr(appearance, "audio_payment_url_3", ""),
                5: getattr(appearance, "audio_payment_url_4", ""),
                6: getattr(appearance, "audio_payment_url_5", ""),
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
    messages.error(request, "Le lien de paiement n’est pas encore disponible.")
    return redirect("catalogue:conversion-audio")


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("catalogue:sitemap"))
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /ckeditor/",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    def _abs(url):
        return request.build_absolute_uri(url)

    def _lastmod(value):
        if not value:
            return ""
        try:
            return value.date().isoformat()
        except Exception:
            try:
                return value.isoformat()[:10]
            except Exception:
                return ""

    url_items = []

    # Pages principales
    static_names = [
        "index",
        "catalogue",
        "livres-numeriques",
        "livres-papier",
        "livres-audio",
        "auteurs",
        "collections",
        "contact",
        "a-propos",
        "nos-contrats",
        "soumission-manuscrit",
        "actualites",
        "conversion-audio",
        "conversion-audio-synthetique",
        "conversion-audio-humain",
        "search",
        "mentions-legales",
        "confidentialite",
        "cookies",
    ]

    for name in static_names:
        try:
            url_items.append((_abs(reverse(f"catalogue:{name}")), ""))
        except Exception:
            continue

    # Pages dynamiques
    for livre in Livre.objects.filter(est_publie=True):
        url_items.append((_abs(livre.get_absolute_url()), _lastmod(livre.updated_at)))

    for auteur in Auteur.objects.all():
        url_items.append((_abs(auteur.get_absolute_url()), _lastmod(auteur.updated_at)))

    for actualite in Actualite.objects.filter(est_publie=True):
        url_items.append((_abs(actualite.get_absolute_url()), _lastmod(actualite.updated_at)))

    for collection in Collection.objects.filter(est_active=True):
        url_items.append((_abs(collection.get_absolute_url()), _lastmod(collection.updated_at)))

    reserved_slugs = {
        "accueil",
        "contact",
        "a-propos",
        "nos-contrats",
        "soumission-manuscrit",
        "conversion-texte-audio",
        "conversion-texte-audio-synthetique",
        "conversion-texte-audio-humain",
        "conversion-texte-audio-choix",
        "mentions-legales",
        "confidentialite",
        "cookies",
        "recherche",
    }

    for page in Page.objects.filter(is_active=True).exclude(slug__in=reserved_slugs):
        try:
            url_items.append((_abs(page.get_absolute_url()), _lastmod(page.updated_at)))
        except Exception:
            continue

    # Build XML
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod in url_items:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return HttpResponse("\n".join(lines), content_type="application/xml")


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
            "Compte créé. Un email de confirmation vous a été envoyé. Activez votre compte pour continuer.",
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
        messages.success(request, "Votre compte est activé. Vous pouvez utiliser le service.")
        return redirect("catalogue:conversion-audio")
    messages.error(request, "Lien d’activation invalide ou expiré.")
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
            messages.error(self.request, "Identifiants invalides.")
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
        if email:
            inscription, created = InscriptionNewsletter.objects.get_or_create(
                email=email,
                defaults={"est_actif": True},
            )
            if created:
                messages.success(request, "Merci ! Vous \u00eates inscrit \u00e0 notre newsletter.")
            else:
                if not inscription.est_actif:
                    inscription.est_actif = True
                    inscription.save()
                    messages.success(request, "Votre inscription a \u00e9t\u00e9 r\u00e9activ\u00e9e.")
                else:
                    messages.info(request, "Vous \u00eates d\u00e9j\u00e0 inscrit.")
        else:
            messages.error(request, "Veuillez saisir une adresse email valide.")

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
            messages.success(request, "Votre message a \u00e9t\u00e9 envoy\u00e9 avec succ\u00e8s.")
            return redirect("catalogue:contact")
        messages.error(request, "Veuillez remplir tous les champs obligatoires.")

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


