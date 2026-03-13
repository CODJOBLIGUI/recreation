from django.db import migrations
from django.utils.text import slugify


def backfill_collection_slugs(apps, schema_editor):
    Collection = apps.get_model("catalogue", "Collection")
    db_alias = schema_editor.connection.alias

    for collection in Collection.objects.using(db_alias).all():
        if collection.slug:
            continue
        base_slug = slugify(collection.nom)
        slug = base_slug
        counter = 1
        while Collection.objects.using(db_alias).filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        collection.slug = slug
        collection.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0012_collection_model_and_livre_fk"),
    ]

    operations = [
        migrations.RunPython(backfill_collection_slugs),
    ]
