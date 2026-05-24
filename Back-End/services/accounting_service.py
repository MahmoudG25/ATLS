from apps.accounting.models import Expense, Revenue, Salary, Invoice, InvoiceItem
from django.db import transaction


def get_expenses(company):
    return Expense.objects.filter(company=company).order_by("-date")


def create_expense(data, company):
    data["company"] = company
    return Expense.objects.create(**data)


def get_revenues(company):
    return Revenue.objects.filter(company=company).order_by("-date")


def create_revenue(data, company):
    data["company"] = company
    return Revenue.objects.create(**data)


def get_salaries(company):
    return Salary.objects.filter(company=company).select_related("employee").order_by("-date")


def create_salary(data, company):
    data["company"] = company
    return Salary.objects.create(**data)


def get_invoices(company):
    return Invoice.objects.filter(company=company).order_by("-issue_date")


def get_invoice_details(invoice_id, company):
    return Invoice.objects.get(id=invoice_id, company=company)


@transaction.atomic
def create_invoice(data, items_data, company, user):
    data["company"] = company
    data["created_by"] = user
    
    invoice = Invoice.objects.create(**data)
    
    total_amount = 0
    for item in items_data:
        item["invoice"] = invoice
        item["company"] = company
        inv_item = InvoiceItem(**item)
        inv_item.save()  # computes item.total
        total_amount += inv_item.total
        
    invoice.total_amount = total_amount
    invoice.save()
    return invoice


def update_invoice_status(invoice_id, status, company):
    invoice = Invoice.objects.get(id=invoice_id, company=company)
    invoice.status = status
    invoice.save()
    return invoice


def get_financial_summary(company):
    expenses = sum([e.amount for e in get_expenses(company)])
    revenues = sum([r.amount for r in get_revenues(company)])
    salaries = sum([s.amount for s in get_salaries(company)])
    
    # Paid sales invoices count as revenue
    sales_invoices = Invoice.objects.filter(company=company, type="sales", status="paid")
    invoiced_revenue = sum([i.total_amount for i in sales_invoices])
    
    # Paid purchase invoices count as expense
    purchase_invoices = Invoice.objects.filter(company=company, type="purchase", status="paid")
    invoiced_expense = sum([i.total_amount for i in purchase_invoices])
    
    total_rev = revenues + invoiced_revenue
    total_exp = expenses + invoiced_expense
    
    return {
        "total_revenue": total_rev,
        "total_expense": total_exp,
        "total_salaries": salaries,
        "net": total_rev - total_exp - salaries,
    }

