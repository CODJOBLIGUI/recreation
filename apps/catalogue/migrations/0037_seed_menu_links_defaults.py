# -*- coding: utf-8 -*-
from django.db import migrations


def seed_menu_links(apps, schema_editor):
    MenuLink = apps.get_model("catalogue", "MenuLink")
    if MenuLink.objects.filter(location="header").exists():
        return
    items = [
        ("Accueil", "/", 1),
        ("Actualités", "/actualites/", 2),
        ("Auteurs", "/auteurs/", 3),
        ("Catalogue", "/catalogue/", 4),
        ("Nos contrats", "/nos-contrats/", 5),
        ("Conversion de texte en audio", "/conversion-texte-audio/", 6),
        ("A propos", "/a-propos/", 7),
        ("Contacts", "/contact/", 8),
        ("Espace des membres du Comité de lecture", "/lecture-evaluation-des-soumissions-de-manuscrit-ou-tapuscrits/", 9),
    ]
    for title, url, order in items:
        MenuLink.objects.get_or_create(
            title=title,
            url=url,
            location="header",
            defaults={"order": order, "is_active": True},
        )


def unseed_menu_links(apps, schema_editor):
    MenuLink = apps.get_model("catalogue", "MenuLink")
    MenuLink.objects.filter(location="header").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0036_committee_application"),
    ]

    operations = [
        migrations.RunPython(seed_menu_links, unseed_menu_links),
    ]
