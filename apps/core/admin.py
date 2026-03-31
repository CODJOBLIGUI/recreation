from django.contrib import admin

from .models import SiteAppearance, SiteContent


@admin.register(SiteAppearance)
class SiteAppearanceAdmin(admin.ModelAdmin):
    list_display = ("site_name",)
    fieldsets = (
        (
            "SEO global",
            {
                "fields": (
                                                                            )
            },
        ),
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
        (
            "Normalisation TTS",
            {
                "fields": (
                    "tts_use_normalization",
                    "tts_spell_unknown",
                    "tts_acronyms",
                )
            },
        ),
        ("Contact", {"fields": ("site_email",)}),
    )


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    fieldsets = (
        (
            "SEO global",
            {
                "fields": (
                                                                            )
            },
        ),
        (
            "En-tête",
            {
                "fields": (
                    "header_search_placeholder",
                    "header_search_button",
                    "newsletter_placeholder",
                    "newsletter_button_label",
                )
            },
        ),
        (
            "SEO sections",
            {
                "fields": (
                    "home_meta_keywords",
                    "contact_meta_keywords",
                    "catalogue_meta_keywords",
                    "actualites_meta_keywords",
                    "auteurs_meta_keywords",
                    "a_propos_meta_keywords",
                    "nos_contrats_meta_keywords",
                    "soumission_meta_keywords",
                    "conversion_meta_keywords",
                )
            },
        ),
        (
            "Navigation",
            {
                "fields": (
                    "nav_brand_label",
                    "nav_menu_label",
                    "nav_drawer_title",
                    "nav_drawer_collections_title",
                    "nav_drawer_formats_title",
                    "nav_drawer_services_title",
                    "nav_drawer_books_digital_label",
                    "nav_drawer_books_audio_label",
                    "nav_drawer_books_print_label",
                    "nav_drawer_conversion_label",
                    "nav_drawer_committee_label",
                    "nav_drawer_social_title",
                    "nav_drawer_shop_label",
                    "nav_cta_title",
                    "nav_cta_text",
                    "nav_cta_button",
                )
            },
        ),
        (
            "Accueil",
            {
                "fields": (
                    "home_carousel_cta_label",
                    "home_section_nouveautes_title",
                    "home_section_bestsellers_title",
                    "home_section_upcoming_title",
                    "home_section_news_title",
                    "home_news_cta_label",
                    "home_newsletter_title",
                    "home_newsletter_button_label",
                    "home_card_cta_label",
                    "home_upcoming_cta_label",
                    "home_tabs_all",
                    "home_tabs_roman",
                    "home_tabs_poemes",
                    "home_tabs_essai",
                    "home_tabs_polars",
                    "home_tabs_bd",
                    "home_tabs_theatres",
                    "home_tabs_nouvelles",
                    "catalogue_page_title",
                    "catalogue_page_subtitle",
                    "catalogue_search_placeholder",
                    "catalogue_search_button_label",
                    "actualites_page_title",
                    "actualites_page_subtitle",
                    "actualites_read_more_label",
                    "actualites_filter_type_label",
                    "actualites_filter_year_label",
                    "actualites_filter_month_label",
                    "actualites_filter_apply_label",
                    "actualites_filter_reset_label",
                    "auteurs_page_title",
                    "auteurs_page_subtitle",
                    "auteurs_filter_placeholder",
                    "auteurs_filter_button_label",
                    "auteurs_card_cta_label",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "contact_title",
                    "contact_subtitle",
                    "contact_address_label",
                    "contact_address_text",
                    "contact_phone_label",
                    "contact_phone_display",
                    "contact_phone_link",
                    "contact_email_label",
                    "contact_email_value",
                    "contact_form_title",
                    "contact_submit_label",
                )
            },
        ),
        (
            "Comit? de lecture",
            {
                "fields": (
                    "committee_login_brand_title",
                    "committee_login_brand_subtitle",
                    "committee_login_title",
                    "committee_login_text_primary",
                    "committee_login_text_secondary",
                    "committee_signup_title",
                    "committee_signup_intro",
                    "committee_signup_confidentiality_text",
                    "committee_signup_motivation_label",
                    "committee_signup_unpaid_label",
                    "committee_signup_submit_label",
                )
            },
        ),
        (
            "Pied de page",
            {
                "fields": (
                    "footer_slogan",
                    "footer_address",
                    "footer_action_phone_label",
                    "footer_action_submit_label",
                    "footer_action_email_label",
                    "footer_social_title",
                    "footer_catalogue_title",
                    "footer_collections_title",
                    "footer_audio_cta_label",
                    "footer_shop_cta_label",
                    "footer_resources_title",
                    "footer_contact_link_label",
                    "footer_link_catalogue",
                    "footer_link_livres_numeriques",
                    "footer_link_livres_audio",
                    "footer_link_livres_papier",
                    "footer_link_actualites",
                    "footer_link_auteurs",
                    "footer_link_a_propos",
                    "footer_link_nouveautes",
                    "footer_link_a_paraitre",
                    "footer_link_meilleures_ventes",
                    "footer_link_nos_contrats",
                    "footer_link_equipe",
                    "footer_link_devenir_auteur",
                    "footer_link_rejoindre_comite",
                    "footer_link_mentions",
                    "footer_link_confidentialite",
                    "footer_link_cookies",
                    "footer_copyright_text",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        # Singleton: un seul enregistrement
        return not SiteContent.objects.exists()
