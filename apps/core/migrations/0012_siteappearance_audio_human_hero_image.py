from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_siteappearance_footer_copyright"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteappearance",
            name="audio_human_hero_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="branding/%Y/%m/",
                verbose_name="Image hero (lecture par un humain)",
            ),
        ),
    ]
