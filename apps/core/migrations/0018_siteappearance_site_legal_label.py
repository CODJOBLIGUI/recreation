from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0017_siteappearance_site_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteappearance",
            name="site_legal_label",
            field=models.CharField(blank=True, max_length=120, verbose_name="Libellé siège social (mentions légales)"),
        ),
    ]
