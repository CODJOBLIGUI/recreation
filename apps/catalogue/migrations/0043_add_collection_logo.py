from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0042_audioconversiongenerated_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="collection",
            name="logo",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="collections/logos/%Y/%m/",
                verbose_name="Logo",
            ),
        ),
    ]
