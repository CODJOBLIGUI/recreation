from django.db import migrations


def add_page(apps, schema_editor):
    Page = apps.get_model("catalogue", "Page")
    Page.objects.get_or_create(
        slug="conversion-texte-audio",
        defaults={
            "title": "Conversion de texte en audio",
            "hero_title": "Conversion de texte en audio",
            "hero_subtitle": "Transformez vos textes en audio en quelques clics",
            "body": "",
            "is_active": True,
        },
    )


def remove_page(apps, schema_editor):
    Page = apps.get_model("catalogue", "Page")
    Page.objects.filter(slug="conversion-texte-audio").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0021_add_audio_conversion_menulink"),
    ]

    operations = [
        migrations.RunPython(add_page, remove_page),
    ]
