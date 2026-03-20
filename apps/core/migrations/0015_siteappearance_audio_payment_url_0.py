from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0014_alter_siteappearance_audio_human_hero_image_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteappearance",
            name="audio_payment_url_0",
            field=models.URLField(blank=True, verbose_name="Paiement audio (1 à 50 pages)"),
        ),
        migrations.AddField(
            model_name="siteappearance",
            name="audio_human_payment_url_0",
            field=models.URLField(blank=True, verbose_name="Paiement lecture par un humain (1 à 50 pages)"),
        ),
    ]
