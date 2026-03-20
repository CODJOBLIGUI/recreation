from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0015_siteappearance_audio_payment_url_0"),
    ]

    operations = [
        migrations.AlterField(
            model_name="siteappearance",
            name="audio_payment_url_1",
            field=models.URLField(blank=True, verbose_name="Paiement audio (51 à 100 pages)"),
        ),
        migrations.AlterField(
            model_name="siteappearance",
            name="audio_human_payment_url_1",
            field=models.URLField(blank=True, verbose_name="Paiement lecture par un humain (51 à 100 pages)"),
        ),
    ]
