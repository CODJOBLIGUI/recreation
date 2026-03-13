from django.db import migrations


def seed_pages(apps, schema_editor):
    Page = apps.get_model("catalogue", "Page")

    defaults = [
        ("Accueil", "accueil"),
        ("Contact", "contact"),
        ("A propos", "a-propos"),
        ("Nos contrats", "nos-contrats"),
        ("Mentions légales", "mentions-legales"),
        ("Confidentialité", "confidentialite"),
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


def unseed_pages(apps, schema_editor):
    Page = apps.get_model("catalogue", "Page")
    slugs = [
        "accueil",
        "contact",
        "a-propos",
        "nos-contrats",
        "mentions-legales",
        "confidentialite",
        "cookies",
    ]
    Page.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0016_add_digital_audio_menulinks"),
    ]

    operations = [
        migrations.RunPython(seed_pages, unseed_pages),
    ]
