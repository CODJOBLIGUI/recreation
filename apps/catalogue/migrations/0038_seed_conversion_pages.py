from django.db import migrations


def create_conversion_pages(apps, schema_editor):
    Page = apps.get_model("catalogue", "Page")

    pages = [
        {
            "slug": "conversion-texte-audio-synthetique",
            "title": "Conversion de texte en audio (synthétique)",
            "hero_title": "Conversion synthétique",
            "hero_subtitle": "Transformez vos textes en audio grâce à la synthèse vocale.",
        },
        {
            "slug": "conversion-texte-audio-humain",
            "title": "Lecture par un humain",
            "hero_title": "Lecture par un humain",
            "hero_subtitle": "Confiez votre texte à un membre de notre équipe pour une lecture par un humain.",
        },
        {
            "slug": "conversion-texte-audio-choix",
            "title": "Conversion de texte en audio",
            "hero_title": "Conversion de texte en audio",
            "hero_subtitle": "Choisissez le type de conversion qui vous convient.",
        },
    ]

    for data in pages:
        Page.objects.get_or_create(
            slug=data["slug"],
            defaults={
                "title": data["title"],
                "hero_title": data["hero_title"],
                "hero_subtitle": data["hero_subtitle"],
                "body": "",
                "is_active": True,
            },
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0037_page_hero_image_and_sitead"),
    ]

    operations = [
        migrations.RunPython(create_conversion_pages, noop_reverse),
    ]
