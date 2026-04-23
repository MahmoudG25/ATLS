from django.db import models
from django.contrib.auth import get_user_model
from apps.farm.models import Sector, Plot

User = get_user_model()

class DailyReport(models.Model):
    engineer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_reports')
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='daily_reports')
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='daily_reports', null=True, blank=True)
    operation_type = models.CharField(max_length=100)
    date = models.DateField()
    workers = models.PositiveIntegerField()
    notes = models.TextField(null=True, blank=True)
    images = models.JSONField(default=list, blank=True)
