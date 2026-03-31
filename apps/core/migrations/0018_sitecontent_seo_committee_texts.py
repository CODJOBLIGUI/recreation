from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_seed_tts_acronyms"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitecontent",
            name="default_meta_title",
            field=models.CharField(
                blank=True,
                default="Editions Recréation - Maison d'édition généraliste",
                max_length=120,
                verbose_name="Meta title par défaut",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="default_meta_description",
            field=models.TextField(
                blank=True,
                default="Editions Recréation, maison d'édition généraliste. Découvrez nos livres papier, numériques et audio.",
                max_length=200,
                verbose_name="Meta description par défaut",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="committee_login_brand_title",
            field=models.CharField(
                blank=True,
                default="Editions Recréation",
                max_length=120,
                verbose_name="Comité - Titre marque",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="committee_login_brand_subtitle",
            field=models.CharField(
                blank=True,
                default="Membres du Comité de lecture",
                max_length=160,
                verbose_name="Comité - Sous-titre marque",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="committee_login_title",
            field=models.CharField(
                blank=True,
                default="Connexion",
                max_length=80,
                verbose_name="Comité - Titre connexion",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="committee_login_text_primary",
            field=models.CharField(
                blank=True,
                default="Connectez-vous pour accéder à l’espace des membres du Comité de lecture.",
                max_length=220,
                verbose_name="Comité - Texte connexion 1",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="committee_login_text_secondary",
            field=models.CharField(
                blank=True,
                default="Si vous n’avez pas encore un compte évaluateur, inscrivez-vous.",
                max_length=200,
                verbose_name="Comité - Texte connexion 2",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="committee_signup_title",
            field=models.CharField(
                blank=True,
                default="Inscription évaluateur",
                max_length=120,
                verbose_name="Comité - Titre inscription",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="committee_signup_intro",
            field=models.TextField(
                blank=True,
                default="Veuillez compléter ce formulaire afin de soumettre votre demande d'accès. Votre demande fera l'objet d'une analyse par un administrateur. Une fois la conformité de votre profil à nos critères validée, votre compte sera activé.",
                verbose_name="Comité - Introduction inscription",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="committee_signup_confidentiality_text",
            field=models.TextField(
                blank=True,
                default="Votre inscription implique votre accord pour garantir la confidentialité des données personnelles de nos auteurs et de tous les fichiers dont vous auriez connaissance, afin d’empêcher toute divulgation à des tiers. Les fichiers téléchargés lors de l’évaluation des dossiers d’édition ne doivent en aucun cas être conservés. La suppression est impérative dans un délai inférieur à une semaine. Prenez-vous acte de ces dispositions et consentez-vous à en respecter strictement toutes les clauses ?",
                verbose_name="Comité - Texte confidentialité",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="committee_signup_motivation_label",
            field=models.CharField(
                blank=True,
                default="Qu’est-ce qui vous motive à rejoindre l’équipe des membres du Comité de lecture des éditions Recréation ?",
                max_length=220,
                verbose_name="Comité - Question motivation",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="committee_signup_unpaid_label",
            field=models.CharField(
                blank=True,
                default="Cette mission n’est pas rémunérée. En avez-vous conscience et êtes-vous toujours partant pour nous rejoindre ?",
                max_length=200,
                verbose_name="Comité - Question mission non rémunérée",
            ),
        ),
        migrations.AddField(
            model_name="sitecontent",
            name="committee_signup_submit_label",
            field=models.CharField(
                blank=True,
                default="Envoyer la demande",
                max_length=80,
                verbose_name="Comité - Bouton inscription",
            ),
        ),
    ]
