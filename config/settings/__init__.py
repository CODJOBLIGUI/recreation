"""
Settings package for editions_recreation.

Automatically loads the appropriate settings module based on DJANGO_ENV.
If DJANGO_ENV is not set, defaults to development settings.
"""
import os

# Determine which settings module to use
env = os.getenv('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
elif env == 'development':
    from .development import *
else:
    from .development import *

