from apps.hr.models import Employee, LeaveRequest, Attendance
from rest_framework.exceptions import ValidationError


def list_employees(status=None):
    qs = Employee.objects.select_related("user").all()
    if status:
        qs = qs.filter(status=status)
    return qs


def get_employee(employee_id):
    return Employee.objects.select_related("user").get(id=employee_id)


def create_employee(data):
    return Employee.objects.create(**data)


def update_employee(employee_id, data):
    employee = Employee.objects.get(id=employee_id)
    for key, value in data.items():
        setattr(employee, key, value)
    employee.save()
    return employee


def list_leave_requests(employee_id=None, status=None):
    qs = LeaveRequest.objects.select_related("employee__user", "reviewed_by").all()
    if employee_id:
        qs = qs.filter(employee_id=employee_id)
    if status:
        qs = qs.filter(status=status)
    return qs


def create_leave_request(data):
    if (
        data.get("end_date")
        and data.get("start_date")
        and data["end_date"] < data["start_date"]
    ):
        raise ValidationError({"end_date": "End date cannot be before start date."})
    return LeaveRequest.objects.create(**data)


def review_leave_request(request_id, reviewer, new_status):
    leave = LeaveRequest.objects.get(id=request_id)
    leave.status = new_status
    leave.reviewed_by = reviewer
    leave.save()
    return leave


def list_attendance(employee_id=None, date=None):
    qs = Attendance.objects.select_related("employee__user").all()
    if employee_id:
        qs = qs.filter(employee_id=employee_id)
    if date:
        qs = qs.filter(date=date)
    return qs


def create_attendance(data):
    return Attendance.objects.create(**data)
