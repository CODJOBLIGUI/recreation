from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0019_siteappearance_meta_keywords"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitecontent",
            name="default_meta_keywords",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Mots-clés séparés par des virgules",
                max_length=255,
                verbose_name="Meta keywords par défaut",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="home_meta_keywords",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Meta keywords Accueil"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="contact_meta_keywords",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Meta keywords Contact"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="catalogue_meta_keywords",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Meta keywords Catalogue"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="actualites_meta_keywords",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Meta keywords Actualités"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="auteurs_meta_keywords",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Meta keywords Auteurs"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="a_propos_meta_keywords",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Meta keywords À propos"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="nos_contrats_meta_keywords",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Meta keywords Nos contrats"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="soumission_meta_keywords",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Meta keywords Soumission manuscrit"),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="conversion_meta_keywords",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Meta keywords Conversion audio"),
        ),
    ]
