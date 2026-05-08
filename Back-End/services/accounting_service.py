from apps.accounting.models import Expense, Revenue, Salary


def get_expenses():
    return Expense.objects.all().order_by("-date")


def create_expense(data):
    return Expense.objects.create(**data)


def get_revenues():
    return Revenue.objects.all().order_by("-date")


def create_revenue(data):
    return Revenue.objects.create(**data)


def get_salaries():
    return Salary.objects.select_related("employee").all().order_by("-date")


def create_salary(data):
    return Salary.objects.create(**data)


def get_financial_summary():
    expenses = sum([e.amount for e in get_expenses()])
    revenues = sum([r.amount for r in get_revenues()])
    salaries = sum([s.amount for s in get_salaries()])
    return {
        "total_revenue": revenues,
        "total_expense": expenses,
        "total_salaries": salaries,
        "net": revenues - expenses - salaries,
    }
