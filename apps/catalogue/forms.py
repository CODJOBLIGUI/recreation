"""
FICHIER : apps/catalogue/forms.py
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import MessageContact, InscriptionNewsletter, SoumissionManuscrit, AudioConversionRequest, UserProfile


class ContactForm(forms.ModelForm):
    """Formulaire de contact."""
    
    class Meta:
        model = MessageContact
        fields = ['nom', 'email', 'telephone', 'sujet', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom complet',
                'id': 'name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'votre@email.com',
                'id': 'email'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control phone-input',
                'placeholder': '+229 XX XX XX XX',
                'id': 'phone'
            }),
            'sujet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Objet de votre message',
                'id': 'subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Votre message...',
                'rows': 6,
                'id': 'message'
            }),
        }
        labels = {
            'nom': 'Nom complet',
            'email': 'Email',
            'telephone': 'Téléphone',
            'sujet': 'Sujet',
            'message': 'Message',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marquer les champs obligatoires
        self.fields['nom'].required = True
        self.fields['email'].required = True
        self.fields['sujet'].required = True
        self.fields['message'].required = True
        self.fields['telephone'].required = False


class NewsletterForm(forms.ModelForm):
    """Formulaire d'inscription à la newsletter."""
    
    class Meta:
        model = InscriptionNewsletter
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'newsletter__input',
                'placeholder': 'Votre adresse email',
                'aria-label': 'Email pour newsletter'
            }),
        }
        labels = {
            'email': '',
        }
    
    def clean_email(self):
        """Validation de l'email."""
        email = self.cleaned_data.get('email')
        
        # Vérifier si l'email existe déjà
        if InscriptionNewsletter.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà inscrit à notre newsletter.")
        
        return email


class SoumissionManuscritForm(forms.ModelForm):
    """Formulaire de soumission de manuscrit."""

    class Meta:
        model = SoumissionManuscrit
        fields = [
            'nom_complet',
            'nom_auteur',
            'whatsapp',
            'autre_numero',
            'nationalite',
            'pays_residence',
            'titre_ouvrage',
            'genre_litteraire',
            'type_contrat',
            'synopsis',
            'avantages',
            'inconvenients',
            'fichier_ouvrage',
            'photo_auteur',
            'carte_identite',
        ]
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom et prénom à l’état civil'}),
            'nom_auteur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom ou pseudonyme d’auteur'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control phone-input', 'placeholder': '+229 XX XX XX XX'}),
            'autre_numero': forms.TextInput(attrs={'class': 'form-control phone-input', 'placeholder': 'Autre numéro'}),
            'nationalite': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nationalité'}),
            'pays_residence': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pays de résidence'}),
            'titre_ouvrage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l’ouvrage'}),
            'genre_litteraire': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Genre littéraire'}),
            'type_contrat': forms.Select(attrs={'class': 'form-control'}),
            'synopsis': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Synopsis ou résumé'}),
            'avantages': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Avantages pour les lecteurs'}),
            'inconvenients': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Inconvénients pour les lecteurs'}),
            'fichier_ouvrage': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'photo_auteur': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'carte_identite': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nom_complet': 'Nom et prénom à l’état civil',
            'nom_auteur': 'Nom ou pseudonyme d’auteur',
            'whatsapp': 'Numéro de téléphone WhatsApp',
            'autre_numero': "Autre numéro de l'auteur",
            'nationalite': 'Nationalité',
            'pays_residence': 'Pays de résidence',
            'titre_ouvrage': 'Titre de l’ouvrage',
            'genre_litteraire': 'Genre littéraire',
            'type_contrat': 'Type de contrat souhaité',
            'synopsis': 'Synopsis ou résumé',
            'avantages': 'Avantages pour les lecteurs',
            'inconvenients': 'Inconvénients pour les lecteurs',
            'fichier_ouvrage': 'Fichier de l’ouvrage',
            'photo_auteur': 'Photo HD de l’auteur sans monde autour',
            'carte_identite': 'Carte d’identité en cours de validité',
        }


class AudioConversionForm(forms.ModelForm):
    """Formulaire conversion texte en audio."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = False

    
    class Meta:
        model = AudioConversionRequest
        fields = ["email", "whatsapp", "texte", "fichier", "langue", "voix"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "votre@email.com"}),
            "whatsapp": forms.TextInput(attrs={"class": "form-control phone-input", "placeholder": "+229 XX XX XX XX"}),
            "texte": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": "Collez votre texte ici (5000 caractères gratuits)."}),
            "fichier": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "langue": forms.Select(attrs={"class": "form-control"}),
            "voix": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "email": "Email",
            "whatsapp": "WhatsApp",
            "texte": "Texte",
            "fichier": "Fichier",
            "langue": "Langue",
            "voix": "Vitesse",
        }

    def _count_sentences(self, text):
        import re
        parts = re.split(r"[.!]+", text or "")
        return len([p for p in (part.strip() for part in parts) if p])

    def clean(self):
        cleaned = super().clean()
        texte = (cleaned.get("texte") or "").strip()
        fichier = cleaned.get("fichier")
        email = (cleaned.get("email") or "").strip()
        if not texte and not fichier:
            raise forms.ValidationError("Veuillez coller un texte ou téléverser un fichier.")
        
        paiement_requis = True if fichier else len(texte) > 5000
        if paiement_requis and not email:
            raise forms.ValidationError("Email requis pour les demandes soumises au paiement.")
        return cleaned


class StyledLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Email ou nom d’utilisateur",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Email ou nom d’utilisateur"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].widget.attrs.update({"class": "form-control"})


class StyledSignupForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    phone = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control phone-input"}))
    newsletter_opt_in = forms.BooleanField(required=False, label="S’inscrire à la newsletter")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email


    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get("phone", "")
            profile.newsletter_opt_in = bool(self.cleaned_data.get("newsletter_opt_in"))
            profile.save()
            if profile.newsletter_opt_in:
                InscriptionNewsletter.objects.get_or_create(email=user.email, defaults={"est_actif": True})
        return user
