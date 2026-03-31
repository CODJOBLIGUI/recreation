from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_sitecontent_seo_committee_texts"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteappearance",
            name="site_meta_keywords",
            field=models.CharField(
                blank=True,
                help_text="Mots-clés séparés par des virgules pour le site",
                max_length=255,
                verbose_name="Mots-clés SEO (site)",
            ),
        ),
    ]
