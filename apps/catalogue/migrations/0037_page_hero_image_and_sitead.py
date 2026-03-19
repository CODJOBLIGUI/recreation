from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0036_merge_20260318_1121"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="hero_image",
            field=models.ImageField(
                blank=True,
                help_text="Image affichée dans le hero bleu de la page.",
                null=True,
                upload_to="pages/heroes/%Y/%m/",
                verbose_name="Image du hero",
            ),
        ),
        migrations.CreateModel(
            name="SiteAd",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Date de création")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Date de modification")),
                ("title", models.CharField(blank=True, max_length=200, verbose_name="Titre")),
                ("text", models.CharField(blank=True, max_length=255, verbose_name="Texte court")),
                ("image", models.ImageField(upload_to="ads/%Y/%m/", verbose_name="Image")),
                ("link_url", models.URLField(blank=True, verbose_name="Lien de redirection")),
                ("weight", models.PositiveSmallIntegerField(default=1, verbose_name="Poids de diffusion")),
                ("is_active", models.BooleanField(default=True, verbose_name="Actif")),
                ("starts_at", models.DateTimeField(blank=True, null=True, verbose_name="Début de diffusion")),
                ("ends_at", models.DateTimeField(blank=True, null=True, verbose_name="Fin de diffusion")),
            ],
            options={
                "verbose_name": "Publicité",
                "verbose_name_plural": "Publicités",
                "ordering": ["-created_at"],
            },
        ),
    ]
