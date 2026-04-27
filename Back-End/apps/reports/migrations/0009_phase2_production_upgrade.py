from django.db import migrations, models
import django.db.models.deletion


def backfill_reports_company(apps, schema_editor):
    Company = apps.get_model("users", "Company")
    Operation = apps.get_model("reports", "Operation")
    DailyTaskReport = apps.get_model("reports", "DailyTaskReport")
    CustomFieldDefinition = apps.get_model("reports", "CustomFieldDefinition")
    ReportDropdownOption = apps.get_model("reports", "ReportDropdownOption")
    Attachment = apps.get_model("reports", "Attachment")
    LaborEntry = apps.get_model("reports", "LaborEntry")

    default_company = Company.objects.order_by("id").first()
    if default_company is None:
        default_company = Company.objects.create(name="Default Company", subscription_plan="starter", is_active=True)

    Operation.objects.filter(company__isnull=True).update(company=default_company)
    DailyTaskReport.objects.filter(company__isnull=True).update(company=default_company)
    CustomFieldDefinition.objects.filter(company__isnull=True).update(company=default_company)
    ReportDropdownOption.objects.filter(company__isnull=True).update(company=default_company)
    Attachment.objects.filter(company__isnull=True).update(company=default_company)
    LaborEntry.objects.filter(company__isnull=True).update(company=default_company)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_company_user_company"),
        ("reports", "0008_multitenant_analytics_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="attachment",
            name="company",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="users.company"),
        ),
        migrations.AddField(
            model_name="laborentry",
            name="company",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="users.company"),
        ),
        migrations.AlterField(
            model_name="laborentry",
            name="hours",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name="laborentry",
            name="overtime",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="laborentry",
            name="worker_rate",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="contractor",
            name="rate_per_hour",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name="operation",
            name="name",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterUniqueTogether(
            name="operation",
            unique_together={("company", "name")},
        ),
        migrations.AddIndex(
            model_name="laborentry",
            index=models.Index(fields=["company", "report"], name="reports_lab_company_af9c3c_idx"),
        ),
        migrations.AddIndex(
            model_name="attachment",
            index=models.Index(fields=["company", "uploaded_at"], name="reports_att_company_3d504f_idx"),
        ),
        migrations.RunPython(backfill_reports_company, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="operation",
            name="company",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="operations", to="users.company"),
        ),
        migrations.AlterField(
            model_name="dailytaskreport",
            name="company",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="daily_task_reports", to="users.company"),
        ),
        migrations.AlterField(
            model_name="customfielddefinition",
            name="company",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="custom_field_definitions", to="users.company"),
        ),
        migrations.AlterField(
            model_name="reportdropdownoption",
            name="company",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="report_options", to="users.company"),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="company",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="users.company"),
        ),
        migrations.AlterField(
            model_name="laborentry",
            name="company",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="users.company"),
        ),
    ]
