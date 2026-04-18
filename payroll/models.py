from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    # Example: Store, Warehouse, Head Office
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    # This links an employee record to a Django user account
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    hire_date = models.DateField()
    job_title = models.CharField(max_length=100)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PayrollPeriod(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Approved', 'Approved'),
        ('Paid', 'Paid'),
    ]

    name = models.CharField(max_length=100)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')

    class Meta:
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.name} ({self.month}/{self.year})"


class PayrollEntry(models.Model):
    # This is the key must-have use case: Employee -> many Payroll Entries
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_entries')
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='payroll_entries')

    basic_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    overtime_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pension_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'payroll_period')
        ordering = ['-created_at']

    def gross_pay(self):
        return (self.basic_pay or Decimal('0.00')) + \
               (self.overtime_amount or Decimal('0.00')) + \
               (self.bonus_amount or Decimal('0.00'))

    def total_deductions(self):
        return (self.tax_amount or Decimal('0.00')) + \
               (self.pension_amount or Decimal('0.00')) + \
               (self.other_deductions or Decimal('0.00'))

    def calculated_net_pay(self):
        return self.gross_pay() - self.total_deductions()

    def save(self, *args, **kwargs):
        # Automatically calculate net pay before saving
        self.net_pay = self.calculated_net_pay()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.payroll_period}"


class Payslip(models.Model):
    payroll_entry = models.OneToOneField(PayrollEntry, on_delete=models.CASCADE, related_name='payslip')
    issue_date = models.DateField()
    reference_code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Payslip {self.reference_code}"


class Approval(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='approvals')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE)
    approved_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.payroll_period} - {self.status}"