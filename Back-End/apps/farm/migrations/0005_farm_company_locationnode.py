from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_company_user_company"),
        ("farm", "0004_crop_stage_enclosure"),
    ]

    operations = [
        migrations.AddField(
            model_name="farm",
            name="company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="farms",
                to="users.company",
            ),
        ),
        migrations.CreateModel(
            name="LocationNode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=120)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("STAGE", "Stage"),
                            ("SECTOR", "Sector"),
                            ("ENCLOSURE", "Enclosure"),
                        ],
                        max_length=20,
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "farm",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="location_nodes",
                        to="farm.farm",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="farm.locationnode",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "name", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="locationnode",
            index=models.Index(
                fields=["farm", "type", "is_active"], name="farm_locati_f8d20f_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="locationnode",
            index=models.Index(
                fields=["parent", "is_active"], name="farm_locati_6fa9ce_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="locationnode",
            constraint=models.UniqueConstraint(
                fields=("farm", "parent", "name", "type"),
                name="uniq_location_node_per_parent",
            ),
        ),
    ]
