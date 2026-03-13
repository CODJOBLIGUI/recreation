from django.db import migrations


def ensure_pages(apps, schema_editor):
    Page = apps.get_model("catalogue", "Page")
    defaults = [
        ("Accueil", "accueil"),
        ("Catalogue", "catalogue"),
        ("Auteurs", "auteurs"),
        ("Actualités", "actualites"),
        ("Soumettre un manuscrit", "soumission-manuscrit"),
        ("A propos", "a-propos"),
        ("Nos contrats", "nos-contrats"),
        ("Contact", "contact"),
        ("Mentions legales", "mentions-legales"),
        ("Confidentialite", "confidentialite"),
        ("Cookies", "cookies"),
    ]

    for title, slug in defaults:
        Page.objects.get_or_create(
            slug=slug,
            defaults={
                "title": title,
                "hero_title": "",
                "hero_subtitle": "",
                "body": "",
                "is_active": True,
            },
        )


def remove_pages(apps, schema_editor):
    Page = apps.get_model("catalogue", "Page")
    slugs = [
        "accueil",
        "catalogue",
        "auteurs",
        "actualites",
        "soumission-manuscrit",
        "a-propos",
        "nos-contrats",
        "contact",
        "mentions-legales",
        "confidentialite",
        "cookies",
    ]
    Page.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0019_seed_home_blocks"),
    ]

    operations = [
        migrations.RunPython(ensure_pages, remove_pages),
    ]
