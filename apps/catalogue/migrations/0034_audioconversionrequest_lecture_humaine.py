from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0033_merge_20260318_0504"),
    ]

    operations = [
        migrations.AddField(
            model_name="audioconversionrequest",
            name="lecture_humaine",
            field=models.BooleanField(default=False, verbose_name="Lecture humaine"),
        ),
        migrations.AddField(
            model_name="audioconversionrequest",
            name="voix_humaine",
            field=models.CharField(
                blank=True,
                choices=[("male", "Voix masculine"), ("female", "Voix féminine")],
                default="",
                max_length=10,
                verbose_name="Voix (lecture humaine)",
            ),
        ),
    ]
