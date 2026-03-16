"""
FICHIER : apps/catalogue/views.py
"""

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.db import close_old_connections
from django.contrib.auth.views import LoginView as DjangoLoginView, PasswordResetView as DjangoPasswordResetView
from datetime import date
import unicodedata

from .forms import ContactForm, NewsletterForm, SoumissionManuscritForm, AudioConversionForm, StyledSignupForm, StyledLoginForm
from .utils.audio_conversion import estimate_pages_from_text, count_pages_for_file, extract_text_from_file
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
    AudioConversionChunk,
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
            context["page_title"] = "Accueil | Editions Recr\u00e9ation | Maison d'\u00e9dition g\u00e9n\u00e9raliste"
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
        context["annees_experience"] = max(1, date.today().year - 2023 + 1)
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
        date_debut = self.request.GET.get("date_debut")
        date_fin = self.request.GET.get("date_fin")
        if filtre == "a-la-une":
            qs = qs.filter(est_une_a_la_une=True)
        if annee:
            qs = qs.filter(date_publication__year=annee)
        if date_debut:
            try:
                qs = qs.filter(date_publication__gte=date.fromisoformat(date_debut))
            except ValueError:
                pass
        if date_fin:
            try:
                qs = qs.filter(date_publication__lte=date.fromisoformat(date_fin))
            except ValueError:
                pass
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Actualit\u00e9s - Editions Recr\u00e9ation"
        context["filtre_actuel"] = self.request.GET.get("filtre", "tous")
        context["annee_actuelle"] = self.request.GET.get("annee", "")
        context["date_debut"] = self.request.GET.get("date_debut", "")
        context["date_fin"] = self.request.GET.get("date_fin", "")
        context["annees_actualites"] = (
            Actualite.objects.filter(est_publie=True)
            .dates("date_publication", "year", order="DESC")
        )
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


class AudioConversionView(FormView):
    template_name = "catalogue/conversion-audio.html"
    form_class = AudioConversionForm
    success_url = reverse_lazy("catalogue:conversion-audio")
    login_url = reverse_lazy("catalogue:login")

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
            if context["last_request"]:
                context["last_request_chunks"] = context["last_request"].chunks.all()
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

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            messages.info(request, "Veuillez vous connecter avec un compte client pour utiliser ce service.")
            logout(request)
            return redirect("catalogue:login")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        texte = (form.cleaned_data.get("texte") or "").strip()
        fichier = form.cleaned_data.get("fichier")
        text_length = len(texte)


        demande = form.save(commit=False)
        if self.request.user.is_authenticated:
            demande.user = self.request.user
        demande.phrases_count = 0
        demande.paiement_requis = True if fichier else text_length > FREE_TEXT_LIMIT
        demande.statut = "awaiting_payment" if demande.paiement_requis else "processing"
        if fichier:
            pages_count = count_pages_for_file(fichier)
        else:
            pages_count = estimate_pages_from_text(texte)
        demande.pages_count = pages_count
        if pages_count <= 100:
            demande.payment_tier = 1
        elif pages_count <= 200:
            demande.payment_tier = 2
        elif pages_count <= 500:
            demande.payment_tier = 3
        elif pages_count <= 1000:
            demande.payment_tier = 4
        else:
            demande.payment_tier = 5
        demande.texte = texte
        demande.async_status = "queued"
        demande.async_progress = 0
        demande.async_error = ""
        demande.async_started_at = None
        demande.async_finished_at = None
        demande.save()

        self._start_conversion_async(demande.id)

        self.request.session["audio_request_id"] = demande.id
        if demande.paiement_requis:
            messages.info(self.request, "Conversion en cours. Le paiement est requis pour recevoir l’audio.")
        else:
            messages.info(self.request, "Conversion en cours. Cette page se mettra à jour automatiquement.")
        return redirect(self.success_url)

    def _start_conversion_async(self, demande_id):
        import threading

        def _generate_audio():
            close_old_connections()
            obj = AudioConversionRequest.objects.filter(pk=demande_id).first()
            if not obj:
                return
            obj.async_started_at = timezone.now()
            obj.async_status = "started"
            obj.async_progress = 5
            obj.async_error = ""
            obj.save(update_fields=["async_started_at", "async_status", "async_progress", "async_error", "updated_at"])

            try:
                text = obj.texte or ""
                if obj.fichier and not text.strip():
                    obj.async_progress = 20
                    obj.save(update_fields=["async_progress", "updated_at"])
                    text = extract_text_from_file(obj.fichier)

                if not text.strip():
                    obj.statut = "error"
                    obj.async_status = "failed"
                    obj.async_progress = 100
                    obj.async_error = "Texte vide après extraction."
                    obj.async_finished_at = timezone.now()
                    obj.save(update_fields=["statut", "async_status", "async_progress", "async_error", "async_finished_at", "updated_at"])
                    return

                obj.texte = text
                obj.save(update_fields=["texte", "updated_at"])

                from gtts import gTTS
                import uuid

                pages_count = obj.pages_count or estimate_pages_from_text(text)
                pages_per_chunk = 50
                chars_per_page = max(500, int(len(text) / max(pages_count, 1)))
                chunk_size = chars_per_page * pages_per_chunk

                chunks = []
                start = 0
                while start < len(text):
                    end = min(start + chunk_size, len(text))
                    if end < len(text):
                        cut = text.rfind(" ", start, end)
                        if cut > start + 200:
                            end = cut
                    chunk_text = text[start:end].strip()
                    if chunk_text:
                        chunks.append(chunk_text)
                    start = end

                if not chunks:
                    chunks = [text]

                AudioConversionChunk.objects.filter(request=obj).delete()
                total_chunks = len(chunks)

                for index, chunk_text in enumerate(chunks, start=1):
                    start_page = (index - 1) * pages_per_chunk + 1
                    end_page = min(index * pages_per_chunk, pages_count)
                    chunk = AudioConversionChunk.objects.create(
                        request=obj,
                        order=index,
                        start_page=start_page,
                        end_page=end_page,
                    )

                    slow = True if obj.voix == "slow" else False
                    tts = gTTS(chunk_text, lang=obj.langue, slow=slow)
                    audio_bytes = ContentFile(b"")
                    filename = f"conversion-{uuid.uuid4().hex}-part{index}.mp3"
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    chunk.audio.save(filename, audio_bytes, save=False)
                    chunk.save(update_fields=["audio", "updated_at"])

                    obj.async_progress = int((index / total_chunks) * 100)
                    obj.save(update_fields=["async_progress", "updated_at"])

                obj.async_status = "finished"
                obj.async_progress = 100
                obj.async_finished_at = timezone.now()
                obj.statut = "delivered" if obj.paiement_requis else "free_generated"
                obj.save(update_fields=["statut", "async_status", "async_progress", "async_finished_at", "updated_at"])
            except Exception as exc:
                obj = AudioConversionRequest.objects.filter(pk=demande_id).first()
                if not obj:
                    return
                obj.statut = "error"
                obj.async_status = "failed"
                obj.async_progress = 100
                obj.async_error = str(exc)
                obj.async_finished_at = timezone.now()
                obj.save(update_fields=["statut", "async_status", "async_progress", "async_error", "async_finished_at", "updated_at"])

        threading.Thread(target=_generate_audio, daemon=True).start()


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
    messages.error(request, "Le lien de paiement n’est pas encore disponible.")
    return redirect("catalogue:conversion-audio")


def conversion_status(request, demande_id):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "auth_required"}, status=401)
    demande = get_object_or_404(AudioConversionRequest, id=demande_id)
    if demande.user and demande.user != request.user and not request.user.is_staff:
        return JsonResponse({"ok": False, "error": "forbidden"}, status=403)
    return JsonResponse(
        {
            "ok": True,
            "id": demande.id,
            "status": demande.async_status,
            "progress": demande.async_progress,
            "error": demande.async_error,
            "audio_url": demande.audio.url if demande.audio else "",
            "has_chunks": demande.chunks.filter(audio__isnull=False).exists(),
            "statut": demande.statut,
            "payment_required": demande.paiement_requis,
        }
    )


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
