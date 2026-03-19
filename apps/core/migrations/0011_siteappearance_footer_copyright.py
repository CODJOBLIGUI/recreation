from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_siteappearance_audio_human_payment_urls"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteappearance",
            name="footer_copyright",
            field=models.CharField(
                blank=True,
                help_text="Utilisez {year} pour l'année automatique.",
                max_length=255,
                verbose_name="Mention de copyright (footer)",
            ),
        ),
    ]
