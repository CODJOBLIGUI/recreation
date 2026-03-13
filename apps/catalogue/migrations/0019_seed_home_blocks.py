from django.db import migrations


def seed_home_blocks(apps, schema_editor):
    Page = apps.get_model("catalogue", "Page")
    PageBlock = apps.get_model("catalogue", "PageBlock")

    page = Page.objects.filter(slug="accueil").first()
    if not page:
        return

    if PageBlock.objects.filter(page=page).exists():
        return

    blocks = [
        ("home_carousel", "Carrousel", 1),
        ("home_nouveautes", "Nouveautés", 2),
        ("home_bestsellers", "Meilleures Ventes", 3),
        ("home_parutions", "Prochaines Parutions", 4),
        ("home_actualites", "Suivez l’actualité", 5),
        ("home_newsletter", "Restez informé de nos nouveautés", 6),
    ]

    for block_type, titre, ordre in blocks:
        PageBlock.objects.create(
            page=page,
            block_type=block_type,
            ordre=ordre,
            titre=titre,
            est_actif=True,
        )


def unseed_home_blocks(apps, schema_editor):
    Page = apps.get_model("catalogue", "Page")
    PageBlock = apps.get_model("catalogue", "PageBlock")
    page = Page.objects.filter(slug="accueil").first()
    if not page:
        return
    PageBlock.objects.filter(page=page, block_type__startswith="home_").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0018_alter_livre_langue_publication_pageblock_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_home_blocks, unseed_home_blocks),
    ]
