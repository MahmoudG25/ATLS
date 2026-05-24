import os
import sys
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import Company, User
from services.accounting_service import (
    create_invoice,
    get_invoices,
    get_invoice_details,
    update_invoice_status,
    get_financial_summary
)
from datetime import date

# Find or create a test company and test user
company, _ = Company.objects.get_or_create(name="Test Accounting Company")
user, _ = User.objects.get_or_create(
    email="testaccount@example.com",
    defaults={"name": "Accountant Test", "company": company, "role": "OWNER", "is_approved": True}
)

print("1. Fetching initial financial summary...")
summary_initial = get_financial_summary(company)
print(f"Initial Revenue: {summary_initial['total_revenue']}, Expenses: {summary_initial['total_expense']}")

print("2. Creating sales invoice with 2 items...")
invoice_data = {
    "invoice_number": "INV-2026-001",
    "type": "sales",
    "party_name": "Al-Nour Distributors",
    "issue_date": date.today(),
    "due_date": date.today(),
    "notes": "Payment term: Immediate"
}

items_data = [
    {"description": "Organic Olive Oil 1L", "quantity": 100, "unit_price": 12.50},
    {"description": "Premium Medjool Dates 500g", "quantity": 50, "unit_price": 8.00}
]

invoice = create_invoice(invoice_data, items_data, company, user)
print(f"Created Invoice: {invoice.invoice_number}, Total Amount: {invoice.total_amount}")
assert invoice.total_amount == 1650.00, f"Expected 1650.00, got {invoice.total_amount}"

print("3. Checking if invoice is listed in get_invoices...")
invoices = get_invoices(company)
assert invoice in invoices, "Invoice not listed!"

print("4. Checking financial summary with UNPAID (Draft) invoice (should not affect revenue)...")
summary_draft = get_financial_summary(company)
assert summary_draft["total_revenue"] == summary_initial["total_revenue"]
print("Draft invoice does not affect summary: verified!")

print("5. Marking invoice as PAID...")
update_invoice_status(invoice.id, "paid", company)
print("Invoice status updated to paid.")

print("6. Re-fetching financial summary (should increase revenue by $1650)...")
summary_paid = get_financial_summary(company)
expected_revenue = summary_initial["total_revenue"] + 1650.00
assert summary_paid["total_revenue"] == expected_revenue, f"Expected {expected_revenue}, got {summary_paid['total_revenue']}"
print("Revenue updated dynamically in financial summary: verified!")

# Clean up
invoice.delete()
print("All invoice testing passed and cleaned up successfully!")
