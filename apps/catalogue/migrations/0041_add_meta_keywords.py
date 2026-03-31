from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0040_soumission_audio_request"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="meta_keywords",
            field=models.CharField(blank=True, max_length=255, verbose_name="Mots-clés SEO"),
        ),
        migrations.AddField(
            model_name="collection",
            name="meta_keywords",
            field=models.CharField(blank=True, max_length=255, verbose_name="Mots-clés SEO"),
        ),
        migrations.AddField(
            model_name="auteur",
            name="meta_keywords",
            field=models.CharField(blank=True, max_length=255, verbose_name="Mots-clés SEO"),
        ),
        migrations.AddField(
            model_name="livre",
            name="meta_keywords",
            field=models.CharField(blank=True, max_length=255, verbose_name="Mots-clés SEO"),
        ),
        migrations.AddField(
            model_name="actualite",
            name="meta_keywords",
            field=models.CharField(blank=True, max_length=255, verbose_name="Mots-clés SEO"),
        ),
    ]
