from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_remove_siteappearance_chariow_widget_code_1_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteappearance",
            name="audio_human_payment_url",
            field=models.URLField(blank=True, verbose_name="Lien paiement (lecture humaine)"),
        ),
        migrations.AddField(
            model_name="siteappearance",
            name="audio_human_payment_url_male",
            field=models.URLField(blank=True, verbose_name="Paiement lecture humaine (voix masculine)"),
        ),
        migrations.AddField(
            model_name="siteappearance",
            name="audio_human_payment_url_female",
            field=models.URLField(blank=True, verbose_name="Paiement lecture humaine (voix féminine)"),
        ),
    ]
