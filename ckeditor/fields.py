"""Compatibility shim for old migrations expecting ckeditor.fields.RichTextField."""
from django_ckeditor_5.fields import CKEditor5Field as RichTextField

__all__ = ["RichTextField"]
