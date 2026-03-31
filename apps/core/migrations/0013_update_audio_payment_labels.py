# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_sitecontent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="siteappearance",
            name="audio_payment_url_1",
            field=models.URLField(blank=True, verbose_name="Paiement audio (1 à 50 pages)"),
        ),
        migrations.AlterField(
            model_name="siteappearance",
            name="audio_payment_url_2",
            field=models.URLField(blank=True, verbose_name="Paiement audio (51 à 100 pages)"),
        ),
        migrations.AlterField(
            model_name="siteappearance",
            name="audio_payment_url_3",
            field=models.URLField(blank=True, verbose_name="Paiement audio (101 à 200 pages)"),
        ),
        migrations.AlterField(
            model_name="siteappearance",
            name="audio_payment_url_4",
            field=models.URLField(blank=True, verbose_name="Paiement audio (201 à 500 pages)"),
        ),
        migrations.AlterField(
            model_name="siteappearance",
            name="audio_payment_url_5",
            field=models.URLField(blank=True, verbose_name="Paiement audio (501+ pages)"),
        ),
    ]
