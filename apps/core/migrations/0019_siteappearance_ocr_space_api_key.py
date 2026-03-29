from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_siteappearance_site_legal_label"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteappearance",
            name="ocr_space_api_key",
            field=models.CharField(
                blank=True,
                help_text="Clé API OCR.space pour l'OCR des PDF scannés.",
                max_length=120,
                verbose_name="Clé OCR.space",
            ),
        ),
    ]

