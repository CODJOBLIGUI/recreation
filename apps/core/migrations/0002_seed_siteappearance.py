from django.db import migrations


def seed_siteappearance(apps, schema_editor):
    SiteAppearance = apps.get_model("core", "SiteAppearance")
    if SiteAppearance.objects.exists():
        return

    SiteAppearance.objects.create(
        site_name="Editions Recréation",
        primary_color="#F5F1E8",
        accent_color="#0A18FF",
        accent_dark="#001FD8",
        text_color="#2C2C2C",
        text_light="#4A4A4A",
        light_bg="#F9F7F3",
        dark_bg="#2C2C2C",
        font_heading="'Cormorant Garamond', serif",
        font_body="'Source Serif 4', serif",
        instagram="https://www.instagram.com/editionsrecreation",
        facebook="https://www.facebook.com/profile.php?id=100063943957824",
        x_twitter="https://x.com/Edi_Recreation?s=09",
        tiktok="https://www.tiktok.com/@editionsrecreation",
        linkedin="https://www.linkedin.com/company/editionsrecreation",
        youtube="https://youtube.com/@editionsrecreation",
        whatsapp="https://wa.me/c/22968809777",
    )


def unseed_siteappearance(apps, schema_editor):
    SiteAppearance = apps.get_model("core", "SiteAppearance")
    SiteAppearance.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_siteappearance, reverse_code=unseed_siteappearance),
    ]
