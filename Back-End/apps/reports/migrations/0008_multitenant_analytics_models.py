from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("farm", "0005_farm_company_locationnode"),
        ("users", "0005_company_user_company"),
        ("reports", "0007_alter_dailytaskreport_crop"),
    ]

    operations = [
        migrations.AddField(
            model_name="customfielddefinition",
            name="company",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="custom_field_definitions", to="users.company"),
        ),
        migrations.AddField(
            model_name="dailytaskreport",
            name="company",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="daily_task_reports", to="users.company"),
        ),
        migrations.AddField(
            model_name="dailytaskreport",
            name="farm",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="daily_task_reports", to="farm.farm"),
        ),
        migrations.AddField(
            model_name="dailytaskreport",
            name="location",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="daily_task_reports", to="farm.locationnode"),
        ),
        migrations.AddField(
            model_name="fertilizationreport",
            name="company",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="fertilization_reports", to="users.company"),
        ),
        migrations.AddField(
            model_name="irrigationreport",
            name="company",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="irrigation_reports", to="users.company"),
        ),
        migrations.AddField(
            model_name="operation",
            name="company",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="operations", to="users.company"),
        ),
        migrations.AddField(
            model_name="operation",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="reportdropdownoption",
            name="company",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="report_options", to="users.company"),
        ),
        migrations.AlterUniqueTogether(
            name="reportdropdownoption",
            unique_together={("company", "name", "category")},
        ),
        migrations.AddIndex(
            model_name="dailytaskreport",
            index=models.Index(fields=["company", "report_date"], name="reports_dai_company_d66d6d_idx"),
        ),
        migrations.AddIndex(
            model_name="dailytaskreport",
            index=models.Index(fields=["company", "operation", "report_date"], name="reports_dai_company_4885f8_idx"),
        ),
        migrations.CreateModel(
            name="Contractor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contractors", to="users.company")),
            ],
            options={"ordering": ["name"], "unique_together": {("company", "name")}},
        ),
        migrations.CreateModel(
            name="Attachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file_url", models.URLField(max_length=1000)),
                ("file_type", models.CharField(choices=[("IMAGE", "Image"), ("VIDEO", "Video"), ("FILE", "File")], max_length=20)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("report", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attachments", to="reports.dailytaskreport")),
            ],
        ),
        migrations.CreateModel(
            name="LaborEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("worker_name", models.CharField(max_length=120)),
                ("worker_type", models.CharField(choices=[("COMPANY", "Company"), ("CONTRACTOR", "Contractor")], max_length=20)),
                ("hours", models.FloatField(default=0)),
                ("overtime", models.FloatField(default=0)),
                ("note", models.CharField(blank=True, max_length=255)),
                ("contractor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="labor_entries", to="reports.contractor")),
                ("report", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="labor_entries", to="reports.dailytaskreport")),
            ],
        ),
        migrations.AddIndex(
            model_name="laborentry",
            index=models.Index(fields=["report", "worker_type"], name="reports_lab_report__4f6a8f_idx"),
        ),
    ]
