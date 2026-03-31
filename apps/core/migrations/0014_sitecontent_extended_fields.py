# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_update_audio_payment_labels"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitecontent",
            name="nav_brand_label",
            field=models.CharField(blank=True, default="Recréation", max_length=80, verbose_name="Nom affiché menu"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="nav_drawer_collections_title",
            field=models.CharField(blank=True, default="Collections", max_length=120, verbose_name="Titre collections (menu mobile)"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="nav_drawer_formats_title",
            field=models.CharField(blank=True, default="Autres versions de livres", max_length=120, verbose_name="Titre formats (menu mobile)"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="nav_drawer_services_title",
            field=models.CharField(blank=True, default="Autres services", max_length=120, verbose_name="Titre services (menu mobile)"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="nav_drawer_books_digital_label",
            field=models.CharField(blank=True, default="Livres numériques", max_length=120, verbose_name="Lien livres numeriques (menu mobile)"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="nav_drawer_books_audio_label",
            field=models.CharField(blank=True, default="Livres audio", max_length=120, verbose_name="Lien livres audio (menu mobile)"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="nav_drawer_books_print_label",
            field=models.CharField(blank=True, default="Livres papier", max_length=120, verbose_name="Lien livres papier (menu mobile)"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="nav_drawer_conversion_label",
            field=models.CharField(blank=True, default="Conversion de texte en audio", max_length=180, verbose_name="Lien conversion audio (menu mobile)"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="nav_drawer_committee_label",
            field=models.CharField(blank=True, default="Espace des membres du Comité de lecture", max_length=220, verbose_name="Lien comite lecture (menu mobile)"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_carousel_cta_label",
            field=models.CharField(blank=True, default="Découvrir", max_length=80, verbose_name="CTA carrousel accueil"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_section_nouveautes_title",
            field=models.CharField(blank=True, default="Nouveautés", max_length=80, verbose_name="Titre section nouveautés"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_section_bestsellers_title",
            field=models.CharField(blank=True, default="Meilleures Ventes", max_length=120, verbose_name="Titre section meilleures ventes"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_section_upcoming_title",
            field=models.CharField(blank=True, default="Prochaines Parutions", max_length=120, verbose_name="Titre section prochaines parutions"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_section_news_title",
            field=models.CharField(blank=True, default="Suivez l’actualité", max_length=120, verbose_name="Titre section actualites accueil"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_news_cta_label",
            field=models.CharField(blank=True, default="Lire la suite", max_length=80, verbose_name="CTA actualites accueil"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_newsletter_title",
            field=models.CharField(blank=True, default="Restez informé de nos nouveautés", max_length=160, verbose_name="Titre newsletter accueil"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_newsletter_button_label",
            field=models.CharField(blank=True, default="S'abonner", max_length=80, verbose_name="Bouton newsletter accueil"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_card_cta_label",
            field=models.CharField(blank=True, default="Voir détails", max_length=80, verbose_name="CTA carte livre"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_upcoming_cta_label",
            field=models.CharField(blank=True, default="Découvrir", max_length=80, verbose_name="CTA prochaines parutions"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_tabs_all",
            field=models.CharField(blank=True, default="Toutes", max_length=60, verbose_name="Onglet Toutes"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_tabs_roman",
            field=models.CharField(blank=True, default="Romans", max_length=60, verbose_name="Onglet Romans"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_tabs_poemes",
            field=models.CharField(blank=True, default="Poèmes", max_length=60, verbose_name="Onglet Poemes"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_tabs_essai",
            field=models.CharField(blank=True, default="Essais", max_length=60, verbose_name="Onglet Essais"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_tabs_polars",
            field=models.CharField(blank=True, default="Polars/Thrillers", max_length=80, verbose_name="Onglet Polars"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_tabs_bd",
            field=models.CharField(blank=True, default="BD", max_length=40, verbose_name="Onglet BD"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_tabs_theatres",
            field=models.CharField(blank=True, default="Théâtres", max_length=60, verbose_name="Onglet Theatres"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_tabs_nouvelles",
            field=models.CharField(blank=True, default="Nouvelles", max_length=60, verbose_name="Onglet Nouvelles"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="contact_title",
            field=models.CharField(blank=True, default="Contactez-nous", max_length=120, verbose_name="Titre contact"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="contact_subtitle",
            field=models.CharField(blank=True, default="Une question ? Un projet ? N'hésitez pas à nous contacter.", max_length=200, verbose_name="Sous-titre contact"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="contact_address_label",
            field=models.CharField(blank=True, default="Adresse", max_length=80, verbose_name="Label adresse"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="contact_phone_label",
            field=models.CharField(blank=True, default="Téléphone", max_length=80, verbose_name="Label telephone"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="contact_email_label",
            field=models.CharField(blank=True, default="Email", max_length=80, verbose_name="Label email"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="contact_address_text",
            field=models.CharField(blank=True, default="Bénin | Abomey-Calavi, France | Marseille, avec des Représentants éditoriaux dans 7 autres pays en Afrique.", max_length=240, verbose_name="Adresse contact"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="contact_phone_display",
            field=models.CharField(blank=True, default="(+229) 01 68 80 97 77", max_length=60, verbose_name="Telephone affiche"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="contact_phone_link",
            field=models.CharField(blank=True, default="+22901688097777", max_length=40, verbose_name="Telephone lien"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="contact_email_value",
            field=models.EmailField(blank=True, default="contactedrecreation@gmail.com", max_length=120, verbose_name="Email contact"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="contact_form_title",
            field=models.CharField(blank=True, default="Envoyez-nous un message", max_length=120, verbose_name="Titre formulaire contact"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="contact_submit_label",
            field=models.CharField(blank=True, default="Envoyer le message", max_length=80, verbose_name="Bouton contact"),
        ),        migrations.AddField(
            model_name="sitecontent",
            name="catalogue_page_title",
            field=models.CharField(blank=True, default="Notre Catalogue", max_length=120, verbose_name="Titre catalogue"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="catalogue_page_subtitle",
            field=models.CharField(blank=True, default="Découvrez tous nos livres", max_length=200, verbose_name="Sous-titre catalogue"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="catalogue_search_placeholder",
            field=models.CharField(blank=True, default="Rechercher un livre, auteur...", max_length=200, verbose_name="Placeholder recherche catalogue"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="catalogue_search_button_label",
            field=models.CharField(blank=True, default="Rechercher", max_length=80, verbose_name="Bouton recherche catalogue"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="actualites_page_title",
            field=models.CharField(blank=True, default="Actualités", max_length=120, verbose_name="Titre actualites"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="actualites_page_subtitle",
            field=models.CharField(blank=True, default="Découvrez nos actualités et nos événements du moment.", max_length=200, verbose_name="Sous-titre actualites"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="actualites_read_more_label",
            field=models.CharField(blank=True, default="Lire la suite", max_length=80, verbose_name="CTA actualites"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="actualites_filter_apply_label",
            field=models.CharField(blank=True, default="Appliquer", max_length=60, verbose_name="Bouton appliquer actualites"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="actualites_filter_reset_label",
            field=models.CharField(blank=True, default="Réinitialiser", max_length=80, verbose_name="Bouton reinitialiser actualites"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="actualites_filter_type_label",
            field=models.CharField(blank=True, default="Type d’actualités", max_length=120, verbose_name="Label type actualites"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="actualites_filter_year_label",
            field=models.CharField(blank=True, default="Année", max_length=80, verbose_name="Label annee actualites"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="actualites_filter_month_label",
            field=models.CharField(blank=True, default="Mois", max_length=80, verbose_name="Label mois actualites"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="auteurs_page_title",
            field=models.CharField(blank=True, default="Nos Auteurs", max_length=120, verbose_name="Titre auteurs"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="auteurs_page_subtitle",
            field=models.CharField(blank=True, default="Découvrez les plumes élues au sein de notre maison", max_length=200, verbose_name="Sous-titre auteurs"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="auteurs_filter_button_label",
            field=models.CharField(blank=True, default="Filtrer", max_length=60, verbose_name="Bouton filtre auteurs"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="auteurs_filter_placeholder",
            field=models.CharField(blank=True, default="Toutes les nationalités", max_length=120, verbose_name="Placeholder filtre auteurs"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="auteurs_card_cta_label",
            field=models.CharField(blank=True, default="Voir la bibliographie", max_length=120, verbose_name="CTA auteurs"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_catalogue",
            field=models.CharField(blank=True, default="Catalogue", max_length=80, verbose_name="Lien catalogue"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_livres_numeriques",
            field=models.CharField(blank=True, default="Livres numériques", max_length=120, verbose_name="Lien livres numeriques"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_livres_audio",
            field=models.CharField(blank=True, default="Livres audio", max_length=120, verbose_name="Lien livres audio"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_livres_papier",
            field=models.CharField(blank=True, default="Livres papier", max_length=120, verbose_name="Lien livres papier"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_actualites",
            field=models.CharField(blank=True, default="Actualités", max_length=80, verbose_name="Lien actualites"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_auteurs",
            field=models.CharField(blank=True, default="Auteurs", max_length=80, verbose_name="Lien auteurs"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_a_propos",
            field=models.CharField(blank=True, default="A propos", max_length=80, verbose_name="Lien a propos"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_nouveautes",
            field=models.CharField(blank=True, default="Nouveautés", max_length=80, verbose_name="Lien nouveautes"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_a_paraitre",
            field=models.CharField(blank=True, default="A paraître", max_length=80, verbose_name="Lien a paraitre"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_meilleures_ventes",
            field=models.CharField(blank=True, default="Meilleures ventes", max_length=120, verbose_name="Lien meilleures ventes"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_nos_contrats",
            field=models.CharField(blank=True, default="Nos contrats", max_length=80, verbose_name="Lien nos contrats"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_equipe",
            field=models.CharField(blank=True, default="Equipe", max_length=80, verbose_name="Lien equipe"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_devenir_auteur",
            field=models.CharField(blank=True, default="Devenir auteur", max_length=120, verbose_name="Lien devenir auteur"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_rejoindre_comite",
            field=models.CharField(blank=True, default="Rejoindre notre Comité de lecture", max_length=200, verbose_name="Lien comite lecture"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_mentions",
            field=models.CharField(blank=True, default="Mentions légales", max_length=120, verbose_name="Lien mentions"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_confidentialite",
            field=models.CharField(blank=True, default="Confidentialité", max_length=120, verbose_name="Lien confidentialite"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="footer_link_cookies",
            field=models.CharField(blank=True, default="Cookies", max_length=80, verbose_name="Lien cookies"),
        ),
    ]


