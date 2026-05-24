from rest_framework import serializers
from apps.accounting.models import Expense, Revenue, Salary, Invoice, InvoiceItem


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = "__all__"
        read_only_fields = ["company"]


class RevenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Revenue
        fields = "__all__"
        read_only_fields = ["company"]


class SalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_email = serializers.CharField(source="employee.email", read_only=True)

    class Meta:
        model = Salary
        fields = "__all__"
        read_only_fields = ["company"]


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ["id", "description", "quantity", "unit_price", "total"]
        read_only_fields = ["id", "total", "company"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "type",
            "status",
            "party_name",
            "issue_date",
            "due_date",
            "total_amount",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
            "items",
        ]
        read_only_fields = ["id", "total_amount", "created_by", "created_at", "company"]

