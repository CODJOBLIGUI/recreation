from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_siteappearance_audio_human_hero_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteappearance",
            name="audio_human_payment_url_1",
            field=models.URLField(blank=True, verbose_name="Paiement lecture par un humain (1 à 100 pages)"),
        ),
        migrations.AddField(
            model_name="siteappearance",
            name="audio_human_payment_url_2",
            field=models.URLField(blank=True, verbose_name="Paiement lecture par un humain (101 à 200 pages)"),
        ),
        migrations.AddField(
            model_name="siteappearance",
            name="audio_human_payment_url_3",
            field=models.URLField(blank=True, verbose_name="Paiement lecture par un humain (201 à 500 pages)"),
        ),
        migrations.AddField(
            model_name="siteappearance",
            name="audio_human_payment_url_4",
            field=models.URLField(blank=True, verbose_name="Paiement lecture par un humain (501 à 1000 pages)"),
        ),
        migrations.AddField(
            model_name="siteappearance",
            name="audio_human_payment_url_5",
            field=models.URLField(blank=True, verbose_name="Paiement lecture par un humain (1001+ pages)"),
        ),
    ]
