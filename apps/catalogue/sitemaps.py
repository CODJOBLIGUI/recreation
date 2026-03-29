from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Livre, Auteur

class LivreSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return Livre.objects.public()

    def lastmod(self, obj):
        return obj.updated_at

class AuteurSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7
    protocol = 'https'

    def items(self):
        return Auteur.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return ['catalogue:index', 'catalogue:catalogue', 'catalogue:auteurs', 'catalogue:a-propos', 'catalogue:contact', 'catalogue:actualites']

    def location(self, item):
        return reverse(item)

