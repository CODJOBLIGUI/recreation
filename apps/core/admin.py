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
        ("TTS", {"fields": ("tts_acronyms",)}),
        ("Footer", {"fields": ("footer_copyright",)}),
        ("Contact", {"fields": ("site_email", "site_address", "site_legal_label")}),
    )


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ("id",)
    fieldsets = (
        (
            "SEO global",
            {
                "fields": (
                    "default_meta_title",
                    "default_meta_description",
                    "default_canonical",
                    "og_image",
                )
            },
        ),
        (
            "Newsletter",
            {
                "fields": (
                    "newsletter_title",
                    "newsletter_subtitle",
                    "newsletter_placeholder",
                    "newsletter_button_label",
                )
            },
        ),
        (
            "Pied de page",
            {
                "fields": (
                    "footer_slogan",
                    "footer_address",
                    "footer_copyright",
                    "footer_title_catalogue",
                    "footer_title_collections",
                    "footer_title_resources",
                    "footer_title_services",
                    "footer_social_title",
                    "footer_catalogue_label",
                    "footer_catalogue_news_label",
                    "footer_catalogue_upcoming_label",
                    "footer_action_phone_label",
                    "footer_action_submit_label",
                    "footer_action_email_label",
                    "footer_action_conversion_label",
                    "footer_action_shop_label",
                )
            },
        ),
        (
            "Navigation",
            {
                "fields": (
                    "nav_title_collections",
                    "nav_title_formats",
                    "nav_title_services",
                    "nav_menu_label",
                    "nav_cta_title",
                    "nav_cta_text",
                    "nav_cta_button",
                )
            },
        ),
        (
            "Header",
            {
                "fields": (
                    "header_search_placeholder",
                    "header_search_button",
                )
            },
        ),
        (
            "Conversion audio",
            {
                "fields": (
                    "conversion_hero_note",
                    "conversion_free_limit_text",
                    "conversion_file_payment_text",
                    "conversion_formats_text",
                    "conversion_form_title",
                    "conversion_payment_note_text",
                    "conversion_payment_required_title",
                    "conversion_payment_required_text",
                    "conversion_payment_error_text",
                    "conversion_processing_title",
                    "conversion_processing_text",
                    "conversion_progress_title",
                    "conversion_progress_text",
                    "conversion_audio_ready_title",
                    "conversion_audio_download_label",
                    "conversion_unavailable_free_text",
                    "conversion_unavailable_paid_text",
                    "conversion_free_limit_reached_text",
                    "conversion_limit_cta_paid_label",
                    "conversion_limit_cta_human_label",
                )
            },
        ),
        (
            "Choix conversion",
            {
                "fields": (
                    "conversion_choice_title",
                    "conversion_choice_subtitle",
                    "conversion_choice_synth_title",
                    "conversion_choice_synth_text",
                    "conversion_choice_synth_button",
                    "conversion_choice_human_title",
                    "conversion_choice_human_text",
                    "conversion_choice_human_button",
                )
            },
        ),
        (
            "Emails",
            {
                "fields": (
                    "activation_email_subject",
                    "activation_email_body",
                    "activation_success_message",
                    "activation_invalid_message",
                    "signup_success_message",
                )
            },
        ),
        (
            "Erreurs",
            {
                "fields": (
                    "error_404_title",
                    "error_404_text",
                    "error_500_title",
                    "error_500_text",
                )
            },
        ),
    )
