# -*- coding: utf-8 -*-
from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    def perms_for(model, actions):
        ct = ContentType.objects.get_for_model(model)
        return list(Permission.objects.filter(content_type=ct, codename__in=actions))

    # Models
    SoumissionManuscrit = apps.get_model("catalogue", "SoumissionManuscrit")
    ManuscriptReview = apps.get_model("catalogue", "ManuscriptReview")
    Actualite = apps.get_model("catalogue", "Actualite")
    Auteur = apps.get_model("catalogue", "Auteur")
    Livre = apps.get_model("catalogue", "Livre")
    Collection = apps.get_model("catalogue", "Collection")
    Page = apps.get_model("catalogue", "Page")
    PageBlock = apps.get_model("catalogue", "PageBlock")
    PageBlockItem = apps.get_model("catalogue", "PageBlockItem")
    MenuLink = apps.get_model("catalogue", "MenuLink")
    MessageContact = apps.get_model("catalogue", "MessageContact")
    InscriptionNewsletter = apps.get_model("catalogue", "InscriptionNewsletter")

    # Comite de lecture
    comite, _ = Group.objects.get_or_create(name="ComiteLecture")
    comite_perms = []
    comite_perms += perms_for(SoumissionManuscrit, ["view_soumissionmanuscrit"])
    comite_perms += perms_for(ManuscriptReview, ["view_manuscriptreview", "add_manuscriptreview", "change_manuscriptreview"])
    comite.permissions.set(comite_perms)

    # Editeur
    editeur, _ = Group.objects.get_or_create(name="Editeur")
    editeur_perms = []
    for model in [Actualite, Auteur, Livre, Collection, Page, PageBlock, PageBlockItem, MenuLink]:
        name = model._meta.model_name
        editeur_perms += perms_for(model, [f"view_{name}", f"add_{name}", f"change_{name}"])
    editeur.permissions.set(editeur_perms)

    # Marketing
    marketing, _ = Group.objects.get_or_create(name="Marketing")
    marketing_perms = []
    for model in [InscriptionNewsletter, MessageContact, Actualite]:
        name = model._meta.model_name
        marketing_perms += perms_for(model, [f"view_{name}", f"add_{name}", f"change_{name}"])
    marketing.permissions.set(marketing_perms)


def remove_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["ComiteLecture", "Editeur", "Marketing"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0034_manuscriptreview"),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
