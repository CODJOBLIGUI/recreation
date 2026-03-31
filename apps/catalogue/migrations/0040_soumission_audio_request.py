from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0039_audio_conversion_force_ocr"),
    ]

    operations = [
        migrations.AddField(
            model_name="soumissionmanuscrit",
            name="audio_request",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="soumission_manuscrit",
                to="catalogue.audioconversionrequest",
                verbose_name="Conversion audio",
            ),
        ),
    ]
