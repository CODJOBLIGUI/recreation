# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0035_create_groups"),
    ]

    operations = [
        migrations.CreateModel(
            name="CommitteeApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("cv", models.FileField(upload_to="committee/cv/%Y/%m/", verbose_name="CV")),
                ("motivation", models.TextField(verbose_name="Motivation")),
                ("confidentiality_ack", models.BooleanField(default=False, verbose_name="Accord confidentialite")),
                ("unpaid_ack", models.BooleanField(default=False, verbose_name="Mission non remuneree acceptee")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="committee_application",
                        to="auth.user",
                        verbose_name="Utilisateur",
                    ),
                ),
            ],
            options={
                "verbose_name": "Candidature comite de lecture",
                "verbose_name_plural": "Candidatures comite de lecture",
                "ordering": ["-created_at"],
            },
        ),
    ]
