from django.db import migrations, models
import ckeditor.fields
import django.db.models.deletion


def forwards_copy_collections(apps, schema_editor):
    Livre = apps.get_model("catalogue", "Livre")
    Collection = apps.get_model("catalogue", "Collection")
    db_alias = schema_editor.connection.alias

    cache = {}
    livres = (
        Livre.objects.using(db_alias)
        .exclude(collection__isnull=True)
        .exclude(collection__exact="")
    )
    for livre in livres:
        name = (livre.collection or "").strip()
        if not name:
            continue
        if name.lower() in {"recréation", "recreation"}:
            continue
        collection = cache.get(name)
        if collection is None:
            collection, _ = Collection.objects.using(db_alias).get_or_create(nom=name)
            cache[name] = collection
        livre.collection_fk = collection
        livre.save(update_fields=["collection_fk"])


def backwards_copy_collections(apps, schema_editor):
    Livre = apps.get_model("catalogue", "Livre")
    db_alias = schema_editor.connection.alias

    for livre in Livre.objects.using(db_alias).all():
        if getattr(livre, "collection_fk", None):
            livre.collection = livre.collection_fk.nom
        else:
            livre.collection = ""
        livre.save(update_fields=["collection"])


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0011_update_menulink_titles"),
    ]

    operations = [
        migrations.CreateModel(
            name="Collection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Date de création")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")),
                ("meta_title", models.CharField(blank=True, max_length=255, verbose_name="Titre SEO")),
                ("meta_description", models.TextField(blank=True, max_length=300, verbose_name="Description SEO")),
                ("nom", models.CharField(max_length=150, verbose_name="Nom")),
                ("slug", models.SlugField(blank=True, max_length=200, unique=True, verbose_name="Slug")),
                ("description", ckeditor.fields.RichTextField(blank=True, verbose_name="Description")),
                ("image", models.ImageField(blank=True, null=True, upload_to="collections/%Y/%m/", verbose_name="Image")),
                ("ordre_affichage", models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")),
                ("est_active", models.BooleanField(default=True, verbose_name="Est active")),
            ],
            options={
                "verbose_name": "Collection",
                "verbose_name_plural": "Collections",
                "ordering": ["ordre_affichage", "nom"],
            },
        ),
        migrations.AddField(
            model_name="livre",
            name="collection_fk",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="livres", to="catalogue.collection", verbose_name="Collection"),
        ),
        migrations.RunPython(forwards_copy_collections, backwards_copy_collections),
        migrations.RemoveField(
            model_name="livre",
            name="collection",
        ),
        migrations.RenameField(
            model_name="livre",
            old_name="collection_fk",
            new_name="collection",
        ),
    ]
