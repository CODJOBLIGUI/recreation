from django.db import migrations


DEFAULT_TTS_ACRONYMS = "\n".join(
    [
        "UNESCO=unésco",
        "UNICEF=unicef",
        "ONU=O N U",
        "UN=U N",
        "UE=U E",
        "UEMOA=uémoa",
        "CEDEAO=cédéao",
        "CNSS=C N S S",
        "CIP=C I P",
        "ISBN=I S B N",
        "ISSN=I S S N",
        "PDF=P D F",
        "DOCX=D O C X",
        "PPTX=P P T X",
        "CV=C V",
        "RDC=R D C",
        "USA=U S A",
        "UK=U K",
        "FR=F R",
        "BENIN=Bénin",
        "TTS=T T S",
        "IA=I A",
    ]
)


def seed_acronyms(apps, schema_editor):
    SiteAppearance = apps.get_model("core", "SiteAppearance")
    for appearance in SiteAppearance.objects.all():
        if not appearance.tts_acronyms:
            appearance.tts_acronyms = DEFAULT_TTS_ACRONYMS
            appearance.save(update_fields=["tts_acronyms"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_siteappearance_tts_fields"),
    ]

    operations = [
        migrations.RunPython(seed_acronyms, migrations.RunPython.noop),
    ]
