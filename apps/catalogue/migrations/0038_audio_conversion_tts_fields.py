from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0037_seed_menu_links_defaults"),
    ]

    operations = [
        migrations.AddField(
            model_name="audioconversionrequest",
            name="texte_normalise",
            field=models.TextField(blank=True, verbose_name="Texte normalisé (TTS)"),
        ),
        migrations.AddField(
            model_name="audioconversionrequest",
            name="use_original_text",
            field=models.BooleanField(
                default=False,
                verbose_name="Utiliser le texte original (sans normalisation)",
            ),
        ),
    ]
