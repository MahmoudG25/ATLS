from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers.accounting_serializers import (
    ExpenseSerializer,
    RevenueSerializer,
    SalarySerializer,
    InvoiceSerializer,
    InvoiceItemSerializer
)
from services.accounting_service import (
    get_expenses,
    create_expense,
    get_revenues,
    create_revenue,
    get_salaries,
    create_salary,
    get_financial_summary,
    get_invoices,
    get_invoice_details,
    create_invoice,
    update_invoice_status
)
from permissions.role_permissions import HasModuleAccess, required_module


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasModuleAccess])
@required_module("accounting")
def finance_summary_view(request):
    company = request.user.company
    return Response(get_financial_summary(company))


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
@required_module("accounting")
def expenses_view(request):
    company = request.user.company
    if request.method == "GET":
        return Response(ExpenseSerializer(get_expenses(company), many=True).data)
    elif request.method == "POST":
        serializer = ExpenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = create_expense(serializer.validated_data, company)
        return Response(ExpenseSerializer(obj).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
@required_module("accounting")
def revenues_view(request):
    company = request.user.company
    if request.method == "GET":
        return Response(RevenueSerializer(get_revenues(company), many=True).data)
    elif request.method == "POST":
        serializer = RevenueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = create_revenue(serializer.validated_data, company)
        return Response(RevenueSerializer(obj).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
@required_module("accounting")
def salaries_view(request):
    company = request.user.company
    if request.method == "GET":
        return Response(SalarySerializer(get_salaries(company), many=True).data)
    elif request.method == "POST":
        serializer = SalarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = create_salary(serializer.validated_data, company)
        return Response(SalarySerializer(obj).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, HasModuleAccess])
@required_module("accounting")
def invoices_view(request):
    company = request.user.company
    if request.method == "GET":
        invoices = get_invoices(company)
        return Response(InvoiceSerializer(invoices, many=True).data)
    elif request.method == "POST":
        items_data = request.data.pop("items", [])
        serializer = InvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate items
        validated_items = []
        for item in items_data:
            item_serializer = InvoiceItemSerializer(data=item)
            item_serializer.is_valid(raise_exception=True)
            validated_items.append(item_serializer.validated_data)
            
        obj = create_invoice(serializer.validated_data, validated_items, company, request.user)
        return Response(InvoiceSerializer(obj).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated, HasModuleAccess])
@required_module("accounting")
def invoice_detail_view(request, id):
    company = request.user.company
    if request.method == "GET":
        try:
            invoice = get_invoice_details(id, company)
            return Response(InvoiceSerializer(invoice).data)
        except Exception:
            return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)
    elif request.method == "PATCH":
        status_value = request.data.get("status")
        if not status_value:
            return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = update_invoice_status(id, status_value, company)
            return Response(InvoiceSerializer(obj).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

