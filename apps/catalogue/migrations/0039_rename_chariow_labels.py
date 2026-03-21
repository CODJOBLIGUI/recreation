from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0038_seed_conversion_pages"),
    ]

    operations = [
        migrations.AlterField(
            model_name="livre",
            name="lien_chariow",
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name="Lien Recréation shop (papier)"),
        ),
        migrations.AlterField(
            model_name="livre",
            name="lien_chariow_audio",
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name="Lien Recréation shop (audio)"),
        ),
        migrations.AlterField(
            model_name="livre",
            name="lien_chariow_numerique",
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name="Lien Recréation shop (numérique)"),
        ),
    ]
