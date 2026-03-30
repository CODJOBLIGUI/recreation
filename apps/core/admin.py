from django.contrib import admin

from .models import SiteAppearance, SiteContent


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
                    "audio_payment_url_1",
                    "audio_payment_url_2",
                    "audio_payment_url_3",
                    "audio_payment_url_4",
                    "audio_payment_url_5",
                    "audio_human_payment_url",
                    "audio_human_payment_url_1",
                    "audio_human_payment_url_2",
                    "audio_human_payment_url_3",
                    "audio_human_payment_url_4",
                    "audio_human_payment_url_5",
                    "audio_human_payment_url_6",
                )
            },
        ),
        ("Contact", {"fields": ("site_email",)}),
    )


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    fieldsets = (
        ("En-tête", {"fields": ("header_search_placeholder", "header_search_button", "newsletter_placeholder", "newsletter_button_label")}),
        ("Menu", {"fields": ("nav_menu_label", "nav_drawer_title", "nav_drawer_social_title", "nav_drawer_shop_label", "nav_cta_title", "nav_cta_text", "nav_cta_button")}),
        ("Pied de page", {"fields": ("footer_slogan", "footer_address", "footer_action_phone_label", "footer_action_submit_label", "footer_action_email_label", "footer_social_title", "footer_catalogue_title", "footer_collections_title", "footer_audio_cta_label", "footer_shop_cta_label", "footer_resources_title", "footer_contact_link_label", "footer_copyright_text")}),
    )

    def has_add_permission(self, request):
        # Singleton: un seul enregistrement
        return not SiteContent.objects.exists()
