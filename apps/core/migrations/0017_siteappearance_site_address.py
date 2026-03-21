from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_alter_siteappearance_payment_labels"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteappearance",
            name="site_address",
            field=models.TextField(blank=True, verbose_name="Adresse (footer/contact)"),
        ),
    ]
