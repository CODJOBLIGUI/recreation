# -*- coding: utf-8 -*-
from django.db import migrations


def seed_sitecontent(apps, schema_editor):
    SiteContent = apps.get_model("core", "SiteContent")
    qs = SiteContent.objects.all()
    if qs.exists():
        sc = qs.first()
    else:
        sc = SiteContent.objects.create()
    updated = False
    for field in sc._meta.fields:
        if field.name in ("id", "created_at", "updated_at"):
            continue
        value = getattr(sc, field.name)
        if value in (None, ""):
            default = field.get_default()
            if default not in (None, ""):
                setattr(sc, field.name, default)
                updated = True
    if updated:
        sc.save()


def unseed_sitecontent(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_sitecontent_extended_fields"),
    ]

    operations = [
        migrations.RunPython(seed_sitecontent, unseed_sitecontent),
    ]
