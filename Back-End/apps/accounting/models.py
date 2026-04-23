from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Expense(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=100)
    date = models.DateField()
    notes = models.TextField(null=True, blank=True)

class Revenue(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=100)
    date = models.DateField()

class Salary(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salaries')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.employee.name} — {self.amount}"

class Invoice(models.Model):
    INVOICE_TYPES = [
        ('purchase', 'Purchase Invoice'),
        ('sales', 'Sales Invoice'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=INVOICE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    party_name = models.CharField(max_length=200)
    issue_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invoices')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.invoice_number} — {self.party_name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} x {self.quantity}"

