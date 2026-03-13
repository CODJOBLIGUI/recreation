from django.db import migrations


def seed_pages_menus(apps, schema_editor):
    Page = apps.get_model("catalogue", "Page")
    MenuLink = apps.get_model("catalogue", "MenuLink")

    pages = [
        ("a-propos", "A propos"),
        ("nos-contrats", "Nos contrats"),
        ("mentions-legales", "Mentions legales"),
        ("confidentialite", "Confidentialite"),
        ("cookies", "Cookies"),
    ]
    for slug, title in pages:
        Page.objects.get_or_create(slug=slug, defaults={"title": title, "body": ""})

    header_links = [
        ("Accueil", "/", 1),
        ("Actualites", "/actualites/", 2),
        ("Auteurs", "/auteurs/", 3),
        ("Catalogue", "/catalogue/", 4),
        ("Nos contrats", "/nos-contrats/", 5),
        ("A propos", "/a-propos/", 6),
        ("Contacts", "/contact/", 7),
    ]
    for title, url, order in header_links:
        MenuLink.objects.get_or_create(
            title=title,
            url=url,
            location="header",
            defaults={"order": order, "is_active": True},
        )

    footer_links = [
        ("Mentions legales", "/mentions-legales/", 1),
        ("Confidentialite", "/confidentialite/", 2),
        ("Cookies", "/cookies/", 3),
    ]
    for title, url, order in footer_links:
        MenuLink.objects.get_or_create(
            title=title,
            url=url,
            location="footer",
            defaults={"order": order, "is_active": True},
        )


def unseed_pages_menus(apps, schema_editor):
    Page = apps.get_model("catalogue", "Page")
    MenuLink = apps.get_model("catalogue", "MenuLink")
    Page.objects.filter(slug__in=["a-propos", "nos-contrats", "mentions-legales", "confidentialite", "cookies"]).delete()
    MenuLink.objects.filter(location__in=["header", "footer"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0009_nationalite_drapeau"),
    ]

    operations = [
        migrations.RunPython(seed_pages_menus, reverse_code=unseed_pages_menus),
    ]
