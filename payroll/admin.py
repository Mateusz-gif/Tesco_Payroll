from django.contrib import admin
from .models import Department, Employee, PayrollPeriod, PayrollEntry, Payslip, Approval


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'department', 'job_title', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'month', 'year', 'status']
    list_filter = ['status', 'year']


@admin.register(PayrollEntry)
class PayrollEntryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'payroll_period', 'basic_pay', 'bonus_amount', 'net_pay']
    list_filter = ['payroll_period']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ['reference_code', 'payroll_entry', 'issue_date']


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ['payroll_period', 'approved_by', 'status', 'approved_at']
    list_filter = ['status']