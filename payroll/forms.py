from django import forms
from .models import Department, Employee, PayrollPeriod, PayrollEntry, Approval


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'user',
            'department',
            'first_name',
            'last_name',
            'email',
            'phone',
            'address',
            'hire_date',
            'job_title',
            'basic_salary',
            'is_active',
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PayrollPeriodForm(forms.ModelForm):
    class Meta:
        model = PayrollPeriod
        fields = ['name', 'month', 'year', 'start_date', 'end_date', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PayrollEntryForm(forms.ModelForm):
    class Meta:
        model = PayrollEntry
        fields = [
            'employee',
            'payroll_period',
            'basic_pay',
            'overtime_hours',
            'overtime_amount',
            'bonus_amount',
            'tax_amount',
            'pension_amount',
            'other_deductions',
        ]


class ApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = ['status', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }