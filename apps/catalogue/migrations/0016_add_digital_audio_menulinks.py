from django.db import migrations


def add_menu_links(apps, schema_editor):
    MenuLink = apps.get_model("catalogue", "MenuLink")
    defaults = [
        ("Livres numériques", "/livres-numeriques/", "header", 5),
        ("Livres audio", "/livres-audio/", "header", 6),
    ]
    for title, url, location, order in defaults:
        MenuLink.objects.get_or_create(
            url=url,
            defaults={
                "title": title,
                "location": location,
                "order": order,
                "is_active": True,
            },
        )


def remove_menu_links(apps, schema_editor):
    MenuLink = apps.get_model("catalogue", "MenuLink")
    MenuLink.objects.filter(url__in=["/livres-numeriques/", "/livres-audio/"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0015_prixlitteraire_and_more"),
    ]

    operations = [
        migrations.RunPython(add_menu_links, remove_menu_links),
    ]
