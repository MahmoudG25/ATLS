from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers.accounting_serializers import ExpenseSerializer, RevenueSerializer, SalarySerializer
from services.accounting_service import get_expenses, create_expense, get_revenues, create_revenue, get_salaries, create_salary, get_financial_summary
from permissions.role_permissions import HasModuleAccess

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasModuleAccess])
def finance_summary_view(request):
    return Response(get_financial_summary())

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, HasModuleAccess])
def expenses_view(request):
    if request.method == 'GET':
        return Response(ExpenseSerializer(get_expenses(), many=True).data)
    elif request.method == 'POST':
        serializer = ExpenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = create_expense(serializer.validated_data)
        return Response(ExpenseSerializer(obj).data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, HasModuleAccess])
def revenues_view(request):
    if request.method == 'GET':
        return Response(RevenueSerializer(get_revenues(), many=True).data)
    elif request.method == 'POST':
        serializer = RevenueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = create_revenue(serializer.validated_data)
        return Response(RevenueSerializer(obj).data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, HasModuleAccess])
def salaries_view(request):
    if request.method == 'GET':
        return Response(SalarySerializer(get_salaries(), many=True).data)
    elif request.method == 'POST':
        serializer = SalarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = create_salary(serializer.validated_data)
        return Response(SalarySerializer(obj).data, status=status.HTTP_201_CREATED)
