from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0038_audio_conversion_tts_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="audioconversionrequest",
            name="force_ocr",
            field=models.BooleanField(default=False, verbose_name="Forcer OCR (PDF scanné)"),
        ),
    ]
