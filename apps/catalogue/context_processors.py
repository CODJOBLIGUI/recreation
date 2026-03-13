from apps.core.models import SiteAppearance
from .models import Collection, Livre, MenuLink

def global_context(request):
    """
    Contexte global pour tous les templates.
    """
    appearance = SiteAppearance.objects.first()
    collections = Collection.objects.filter(est_active=True).order_by("ordre_affichage", "nom")

    social_links = [
        {"label": "Instagram", "icon": "fab fa-instagram", "url": appearance.instagram if appearance and appearance.instagram else "https://www.instagram.com/editionsrecreation"},
        {"label": "Facebook", "icon": "fab fa-facebook-f", "url": appearance.facebook if appearance and appearance.facebook else "https://www.facebook.com/profile.php?id=100063943957824"},
        {"label": "X", "icon": "fab fa-x-twitter", "url": appearance.x_twitter if appearance and appearance.x_twitter else "https://x.com/Edi_Recreation?s=09"},
        {"label": "TikTok", "icon": "fab fa-tiktok", "url": appearance.tiktok if appearance and appearance.tiktok else "https://www.tiktok.com/@editionsrecreation"},
        {"label": "LinkedIn", "icon": "fab fa-linkedin-in", "url": appearance.linkedin if appearance and appearance.linkedin else "https://www.linkedin.com/company/editionsrecreation"},
        {"label": "YouTube", "icon": "fab fa-youtube", "url": appearance.youtube if appearance and appearance.youtube else "https://youtube.com/@editionsrecreation"},
        {"label": "WhatsApp", "icon": "fab fa-whatsapp", "url": appearance.whatsapp if appearance and appearance.whatsapp else "https://wa.me/c/22968809777"},
    ]

    menu_header_links = MenuLink.objects.filter(is_active=True, location="header").order_by("order", "title")
    menu_footer_links = MenuLink.objects.filter(is_active=True, location="footer").order_by("order", "title")

    return {
        "categories_list": Livre.CATEGORIES,
        "collections_list": collections,
        "appearance": appearance,
        "social_links": social_links,
        "menu_header_links": menu_header_links,
        "menu_footer_links": menu_footer_links,
    }
