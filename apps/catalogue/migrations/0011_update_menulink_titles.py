from django.db import migrations


def update_menulink_titles(apps, schema_editor):
    MenuLink = apps.get_model("catalogue", "MenuLink")
    MenuLink.objects.filter(url="/actualites/").update(title="Actualités")


def reverse_update_menulink_titles(apps, schema_editor):
    MenuLink = apps.get_model("catalogue", "MenuLink")
    MenuLink.objects.filter(url="/actualites/").update(title="Actualites")


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0010_seed_pages_menus"),
    ]

    operations = [
        migrations.RunPython(update_menulink_titles, reverse_update_menulink_titles),
    ]
