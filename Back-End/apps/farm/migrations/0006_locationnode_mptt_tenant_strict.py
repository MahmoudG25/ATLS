from django.db import migrations, models
import django.db.models.deletion


def backfill_farm_company(apps, schema_editor):
    Company = apps.get_model("users", "Company")
    Farm = apps.get_model("farm", "Farm")
    LocationNode = apps.get_model("farm", "LocationNode")

    default_company = Company.objects.order_by("id").first()
    if default_company is None:
        default_company = Company.objects.create(name="Default Company", subscription_plan="starter", is_active=True)

    Farm.objects.filter(company__isnull=True).update(company=default_company)
    LocationNode.objects.filter(company__isnull=True).update(company=default_company)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_company_user_company"),
        ("farm", "0005_farm_company_locationnode"),
    ]

    operations = [
        migrations.AddField(
            model_name="locationnode",
            name="company",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="users.company"),
        ),
        migrations.AddField(
            model_name="locationnode",
            name="level",
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name="locationnode",
            name="lft",
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name="locationnode",
            name="rght",
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name="locationnode",
            name="tree_id",
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
        ),
        migrations.AlterField(
            model_name="locationnode",
            name="parent",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="children", to="farm.locationnode"),
        ),
        migrations.RemoveConstraint(
            model_name="locationnode",
            name="uniq_location_node_per_parent",
        ),
        migrations.AddConstraint(
            model_name="locationnode",
            constraint=models.UniqueConstraint(fields=("company", "farm", "parent", "name", "type"), name="uniq_location_node_per_parent"),
        ),
        migrations.AddIndex(
            model_name="locationnode",
            index=models.Index(fields=["company", "type", "is_active"], name="farm_locati_company_aeab7b_idx"),
        ),
        migrations.RunPython(backfill_farm_company, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="farm",
            name="company",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="farms", to="users.company"),
        ),
        migrations.AlterField(
            model_name="locationnode",
            name="company",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="users.company"),
        ),
    ]
