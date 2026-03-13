from django.db import migrations


def add_link(apps, schema_editor):
    MenuLink = apps.get_model("catalogue", "MenuLink")
    MenuLink.objects.get_or_create(
        url="/conversion-texte-audio/",
        defaults={
            "title": "Conversion de texte en audio",
            "location": "header",
            "order": 5,
            "is_active": True,
        },
    )


def remove_link(apps, schema_editor):
    MenuLink = apps.get_model("catalogue", "MenuLink")
    MenuLink.objects.filter(url="/conversion-texte-audio/").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0020_ensure_pages_catalogue"),
    ]

    operations = [
        migrations.RunPython(add_link, remove_link),
    ]
