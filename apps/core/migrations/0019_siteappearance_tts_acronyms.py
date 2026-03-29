from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_siteappearance_site_legal_label"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteappearance",
            name="tts_acronyms",
            field=models.TextField(
                blank=True,
                help_text="Ex: ONU, UE, USA, BTP",
                verbose_name="Sigles TTS (separes par des virgules)",
            ),
        ),
    ]

