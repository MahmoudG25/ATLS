from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Employee(models.Model):
    """
    HR Employee record linked to the system User.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    hire_date = models.DateField()
    department = models.CharField(max_length=100, blank=True, default='')
    position = models.CharField(max_length=100, blank=True, default='')
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.user.name} — {self.position}"

class LeaveRequest(models.Model):
    """
    Employee leave/vacation requests.
    """
    LEAVE_TYPES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('personal', 'Personal Leave'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.user.name} — {self.leave_type} ({self.start_date} → {self.end_date})"

class Attendance(models.Model):
    """
    Daily attendance log for employees.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
    ], default='present')
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-date']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.user.name} — {self.date} ({self.status})"
