
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent.parent



SECRET_KEY = os.getenv('SECRET_KEY', '(k*=u_l0=y4c*%=e+i+ecy7l9x#1@eo%_#8y$84fyt_5rhq8c3')


# Application definition

INSTALLED_APPS = [
    'ckeditor',
    'ckeditor_uploader',
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    # Local Apps
    'apps.core',
    'apps.catalogue',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "config/templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'apps.catalogue.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Africa/Porto-Novo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (user-uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CKEditor uploads
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_ALLOW_NONIMAGE_FILES = True
CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 360,
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserImageUploadUrl': '/ckeditor/upload/',
    }
}

# Email (configure via environment for production)
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@editions-recreation.local")


# Auth redirects
LOGIN_REDIRECT_URL = "/conversion-texte-audio/"
LOGOUT_REDIRECT_URL = "/"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



UNFOLD = {
    # -------------------------------------------------------------------------
    # BRANDING
    # -------------------------------------------------------------------------
    "SITE_TITLE": "Editions Recr\u00e9ation",
    "SITE_HEADER": "Administration",
    "SITE_URL": "/",
    
    "SITE_LOGO": {
        "light": "catalogue/images/logo.jpg",
        "dark": "catalogue/images/logo.jpg",
    },
    
    "SITE_SYMBOL": "📚",
    
    # -------------------------------------------------------------------------
    # COULEURS
    # -------------------------------------------------------------------------
    "COLORS": {
        "primary": {
            "50": "255 241 232",
            "100": "245 241 232",
            "200": "224 217 205",
            "300": "180 120 120",
            "400": "160 80 80",
            "500": "139 58 58",     
            "600": "120 50 50",
            "700": "107 40 40",
            "800": "60 30 30",
            "900": "44 44 44",
        },
    },
    
    # -------------------------------------------------------------------------
    # THÈME
    # -------------------------------------------------------------------------
    "THEME": "dark",
    "SHOW_THEMES": True, 
    
    # -------------------------------------------------------------------------
    # MENU LATÉRAL
    # -------------------------------------------------------------------------
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Tableau de bord",
                "separator": False,
                "items": [
                    {
                        "title": "Accueil",
                        "icon": "home",
                        "link": "/admin/",
                    },
                ],
            },
            {
                "title": "Gestion du catalogue",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Livres",
                        "icon": "menu_book",
                        "link": "/admin/catalogue/livre/",
                    },
                    {
                        "title": "Auteurs",
                        "icon": "person",
                        "link": "/admin/catalogue/auteur/",
                    },
                    {
                        "title": "Membres de l'équipe",
                        "icon": "group",
                        "link": "/admin/catalogue/membre/",
                    },
                ],
            },
            {
                "title": "Gestion des pages",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Pages",
                        "icon": "edit_document",
                        "link": "/admin/catalogue/page/",
                    },
                    {
                        "title": "Liens de menu",
                        "icon": "link",
                        "link": "/admin/catalogue/menulink/",
                    },
                    {
                        "title": "A propos (site)",
                        "icon": "info",
                        "link": "/a-propos/",
                    },
                    {
                        "title": "Nos contrats (site)",
                        "icon": "description",
                        "link": "/nos-contrats/",
                    },
                    {
                        "title": "Mentions legales (site)",
                        "icon": "gavel",
                        "link": "/mentions-legales/",
                    },
                ],
            },
            {
                "title": "Communication",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Actualités",
                        "icon": "newspaper",
                        "link": "/admin/catalogue/actualite/",
                    },
                    {
                        "title": "Inscriptions Newsletter",
                        "icon": "mail",
                        "link": "/admin/catalogue/inscriptionnewsletter/",
                        "badge": "new",
                    },
                    {
                        "title": "Messages de contact",
                        "icon": "inbox",
                        "link": "/admin/catalogue/messagecontact/",
                        "badge": "new",
                    },
                ],
            },
            {
                "title": "Administration",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Utilisateurs",
                        "icon": "manage_accounts",
                        "link": "/admin/auth/user/",
                    },
                    {
                        "title": "Groupes",
                        "icon": "verified_user",
                        "link": "/admin/auth/group/",
                    },
                ],
            },
            {
                "title": "Apparence",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Apparence du site",
                        "icon": "palette",
                        "link": "/admin/core/siteappearance/",
                    },
                ],
            },
        ],
    },
    
    # -------------------------------------------------------------------------
    # CSS PERSONNALISÉ (optionnel)
    # -------------------------------------------------------------------------
    "STYLES": [
        lambda request: "catalogue/css/admin-custom.css",
    ],
}
