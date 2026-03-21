from django.contrib import admin

from .models import SiteAppearance


@admin.register(SiteAppearance)
class SiteAppearanceAdmin(admin.ModelAdmin):
    list_display = ("site_name",)
    fieldsets = (
        ("Identite", {"fields": ("site_name", "logo", "favicon")}),
        ("Couleurs", {"fields": ("primary_color", "accent_color", "accent_dark", "text_color", "text_light", "light_bg", "dark_bg")}),
        ("Typographie", {"fields": ("font_heading", "font_body")}),
        ("Reseaux sociaux", {"fields": ("instagram", "facebook", "x_twitter", "tiktok", "linkedin", "youtube", "whatsapp")}),
        (
            "Paiements",
            {
                "fields": (
                    "audio_payment_url",
                    "audio_payment_url_0",
                    "audio_payment_url_1",
                    "audio_payment_url_2",
                    "audio_payment_url_3",
                    "audio_payment_url_4",
                    "audio_payment_url_5",
                    "audio_human_payment_url_0",
                    "audio_human_payment_url_1",
                    "audio_human_payment_url_2",
                    "audio_human_payment_url_3",
                    "audio_human_payment_url_4",
                    "audio_human_payment_url_5",
                )
            },
        ),
        ("Footer", {"fields": ("footer_copyright",)}),
        ("Contact", {"fields": ("site_email", "site_address")}),
    )
