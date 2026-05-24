from rest_framework import serializers
from apps.accounting.models import Expense, Revenue, Salary


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = "__all__"


class RevenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Revenue
        fields = "__all__"


class SalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_email = serializers.CharField(source="employee.email", read_only=True)

    class Meta:
        model = Salary
        fields = "__all__"
