from django.db import migrations, models


def forwards_copy_auteur(apps, schema_editor):
    Livre = apps.get_model("catalogue", "Livre")
    db_alias = schema_editor.connection.alias

    for livre in Livre.objects.using(db_alias).all():
        auteur = getattr(livre, "auteur", None)
        if auteur:
            livre.auteurs.add(auteur)


def backwards_copy_auteur(apps, schema_editor):
    Livre = apps.get_model("catalogue", "Livre")
    db_alias = schema_editor.connection.alias

    for livre in Livre.objects.using(db_alias).all():
        first = livre.auteurs.first()
        if first:
            livre.auteur = first
            livre.save(update_fields=["auteur"])


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0013_backfill_collection_slugs"),
    ]

    operations = [
        migrations.AddField(
            model_name="livre",
            name="auteurs",
            field=models.ManyToManyField(help_text="Sélectionnez un ou plusieurs auteurs.", related_name="livres", to="catalogue.auteur", verbose_name="Auteurs"),
        ),
        migrations.RunPython(forwards_copy_auteur, backwards_copy_auteur),
        migrations.RemoveField(
            model_name="livre",
            name="auteur",
        ),
        migrations.AddIndex(
            model_name="livre",
            index=models.Index(fields=["titre"], name="catalogue_l_titre_idx"),
        ),
    ]
