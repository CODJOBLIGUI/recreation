from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_seed_sitecontent_defaults"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteappearance",
            name="tts_use_normalization",
            field=models.BooleanField(
                default=True,
                help_text="Active la normalisation automatique des sigles et des MAJUSCULES avant conversion audio.",
                verbose_name="Activer la normalisation TTS",
            ),
        ),
        migrations.AddField(
            model_name="siteappearance",
            name="tts_acronyms",
            field=models.TextField(
                blank=True,
                help_text=(
                    "Une entrée par ligne. Format: SIGLE=prononciation. "
                    "Ex: UNESCO=unésco. Si pas de valeur, le sigle sera épelé."
                ),
                verbose_name="Dictionnaire sigles (TTS)",
            ),
        ),
        migrations.AddField(
            model_name="siteappearance",
            name="tts_spell_unknown",
            field=models.BooleanField(
                default=True,
                help_text="Si activé, les sigles inconnus (2-4 lettres) sont épelés.",
                verbose_name="Épeler les sigles inconnus",
            ),
        ),
    ]
