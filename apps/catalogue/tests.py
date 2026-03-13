from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.core.models import SiteAppearance
from .models import AudioConversionRequest
from .forms import SoumissionManuscritForm


class AudioConversionPaymentTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="client", email="client@example.com", password="pass12345")
        self.client.login(username="client", password="pass12345")
        SiteAppearance.objects.create(
            site_name="Editions Recréation",
            audio_payment_url="https://example.com/pay-default",
            audio_payment_url_1="https://example.com/pay-1",
            audio_payment_url_2="https://example.com/pay-2",
            audio_payment_url_3="https://example.com/pay-3",
            audio_payment_url_4="https://example.com/pay-4",
            audio_payment_url_5="https://example.com/pay-5",
        )

    def test_payment_url_uses_page_tier(self):
        texte = "mot " * 1200  # ~1200 mots => ~4 pages
        response = self.client.post(
            reverse("catalogue:conversion-audio"),
            {
                "email": "client@example.com",
                "whatsapp": "+22900000000",
                "texte": texte,
                "langue": "fr",
                "voix": "standard",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("payment_url", response.context)
        self.assertEqual(response.context["payment_url"], "https://example.com/pay-1")

    def test_payment_redirect_uses_tier_url(self):
        demande = AudioConversionRequest.objects.create(
            email="client@example.com",
            whatsapp="",
            texte="x",
            paiement_requis=True,
            statut="awaiting_payment",
            payment_tier=3,
        )
        response = self.client.get(reverse("catalogue:conversion-audio-pay", args=[demande.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "https://example.com/pay-3")


class SoumissionManuscritFormTests(TestCase):
    def test_form_has_new_fields_and_labels(self):
        form = SoumissionManuscritForm()
        self.assertIn("type_contrat", form.fields)
        self.assertIn("whatsapp", form.fields)
        self.assertIn("autre_numero", form.fields)
        self.assertIn("nationalite", form.fields)
        self.assertIn("pays_residence", form.fields)
        self.assertEqual(form.fields["photo_auteur"].label, "Photo HD de l’auteur sans monde autour")
