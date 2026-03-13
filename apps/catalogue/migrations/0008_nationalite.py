from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0007_menulink_page"),
    ]

    operations = [
        migrations.CreateModel(
            name="Nationalite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=120, verbose_name="Nom du pays")),
                ("code_iso", models.CharField(max_length=2, verbose_name="Code ISO (2 lettres)")),
            ],
            options={
                "verbose_name": "Nationalité",
                "verbose_name_plural": "Nationalités",
                "ordering": ["nom"],
            },
        ),
        migrations.AddIndex(
            model_name="nationalite",
            index=models.Index(fields=["nom", "code_iso"], name="catalogue_n_nom_b8d019_idx"),
        ),
        migrations.AddField(
            model_name="auteur",
            name="nationalites",
            field=models.ManyToManyField(
                blank=True,
                help_text="Selectionnez une ou plusieurs nationalites.",
                related_name="auteurs",
                to="catalogue.nationalite",
                verbose_name="Nationalités",
            ),
        ),
    ]
