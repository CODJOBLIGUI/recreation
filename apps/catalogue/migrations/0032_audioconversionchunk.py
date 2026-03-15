from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0031_remove_soumissionmanuscrit_contacts_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AudioConversionChunk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Date de création")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Date de modification")),
                ("order", models.PositiveIntegerField(default=1, verbose_name="Ordre")),
                ("start_page", models.PositiveIntegerField(default=1, verbose_name="Page de début")),
                ("end_page", models.PositiveIntegerField(default=1, verbose_name="Page de fin")),
                ("audio", models.FileField(blank=True, null=True, upload_to="audio_requests/chunks/%Y/%m/", verbose_name="Audio (segment)")),
                ("error", models.TextField(blank=True, verbose_name="Erreur")),
                ("request", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chunks", to="catalogue.audioconversionrequest", verbose_name="Demande")),
            ],
            options={
                "verbose_name": "Segment audio",
                "verbose_name_plural": "Segments audio",
                "ordering": ["order"],
            },
        ),
    ]
