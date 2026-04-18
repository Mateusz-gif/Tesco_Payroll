from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import group_required, is_employee
from .forms import EmployeeForm, PayrollPeriodForm, PayrollEntryForm, ApprovalForm
from .models import Employee, PayrollPeriod, PayrollEntry, Payslip, Approval


@login_required
def home(request):
    # Simple dashboard page
    return render(request, 'payroll/home.html')


# -----------------------------
# Employee views
# -----------------------------

@login_required
@group_required('HR Manager')
def employee_list(request):
    employees = Employee.objects.select_related('department', 'user').all()
    return render(request, 'payroll/employee_list.html', {'employees': employees})


@login_required
@group_required('HR Manager')
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee created successfully.')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'payroll/form.html', {'form': form, 'title': 'Add Employee'})


@login_required
@group_required('HR Manager')
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully.')
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'payroll/form.html', {'form': form, 'title': 'Edit Employee'})


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    # HR can see all employee records
    if request.user.groups.filter(name='HR Manager').exists():
        return render(request, 'payroll/employee_detail.html', {'employee': employee})

    # Employees can only see their own profile
    if hasattr(request.user, 'employee_profile') and request.user.employee_profile.pk == employee.pk:
        return render(request, 'payroll/employee_detail.html', {'employee': employee})

    return HttpResponseForbidden('You are not allowed to view this employee record.')


@login_required
def my_profile(request):
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'No employee profile is linked to your account.')
        return redirect('home')

    employee = request.user.employee_profile
    return render(request, 'payroll/employee_detail.html', {'employee': employee})


# -----------------------------
# Payroll period views
# -----------------------------

@login_required
def payroll_period_list(request):
    # Payroll Officer, Finance Manager and HR can view periods
    allowed = request.user.groups.filter(
        name__in=['Payroll Officer', 'Finance Manager', 'HR Manager']
    ).exists()

    if not allowed:
        return HttpResponseForbidden('You are not allowed to view payroll periods.')

    periods = PayrollPeriod.objects.all()
    return render(request, 'payroll/payroll_period_list.html', {'periods': periods})


@login_required
@group_required('Payroll Officer')
def payroll_period_create(request):
    if request.method == 'POST':
        form = PayrollPeriodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll period created successfully.')
            return redirect('payroll_period_list')
    else:
        form = PayrollPeriodForm()
    return render(request, 'payroll/form.html', {'form': form, 'title': 'Add Payroll Period'})


@login_required
@group_required('Payroll Officer')
def payroll_period_update(request, pk):
    period = get_object_or_404(PayrollPeriod, pk=pk)
    if request.method == 'POST':
        form = PayrollPeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll period updated successfully.')
            return redirect('payroll_period_list')
    else:
        form = PayrollPeriodForm(instance=period)
    return render(request, 'payroll/form.html', {'form': form, 'title': 'Edit Payroll Period'})


# -----------------------------
# Payroll entry views
# -----------------------------

@login_required
def payroll_entry_list(request):
    # Payroll Officer and Finance Manager can see all entries
    if request.user.groups.filter(name__in=['Payroll Officer', 'Finance Manager']).exists():
        entries = PayrollEntry.objects.select_related('employee', 'payroll_period').all()
        return render(request, 'payroll/payroll_entry_list.html', {'entries': entries})

    # Employee can only see their own entries
    if hasattr(request.user, 'employee_profile'):
        entries = PayrollEntry.objects.filter(employee=request.user.employee_profile)
        return render(request, 'payroll/payroll_entry_list.html', {'entries': entries})

    return HttpResponseForbidden('You are not allowed to view payroll entries.')


@login_required
@group_required('Payroll Officer')
def payroll_entry_create(request):
    if request.method == 'POST':
        form = PayrollEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()

            # Automatically create a payslip if one does not exist
            if not hasattr(entry, 'payslip'):
                Payslip.objects.create(
                    payroll_entry=entry,
                    issue_date=entry.payroll_period.end_date,
                    reference_code=f"PS-{entry.payroll_period.year}-{entry.payroll_period.month}-{entry.pk}"
                )

            messages.success(request, 'Payroll entry created successfully.')
            return redirect('payroll_entry_list')
    else:
        form = PayrollEntryForm()
    return render(request, 'payroll/form.html', {'form': form, 'title': 'Add Payroll Entry'})


@login_required
def payroll_entry_detail(request, pk):
    entry = get_object_or_404(PayrollEntry, pk=pk)

    # Payroll Officer and Finance Manager can view all entries
    if request.user.groups.filter(name__in=['Payroll Officer', 'Finance Manager']).exists():
        return render(request, 'payroll/payroll_entry_detail.html', {'entry': entry})

    # Employee can only view their own entry
    if hasattr(request.user, 'employee_profile') and entry.employee == request.user.employee_profile:
        return render(request, 'payroll/payroll_entry_detail.html', {'entry': entry})

    return HttpResponseForbidden('You are not allowed to view this payroll entry.')


# -----------------------------
# Payslip views
# -----------------------------

@login_required
def my_payslips(request):
    if not hasattr(request.user, 'employee_profile'):
        return HttpResponseForbidden('You do not have an employee profile.')

    payslips = Payslip.objects.filter(
        payroll_entry__employee=request.user.employee_profile
    ).select_related('payroll_entry', 'payroll_entry__payroll_period')

    return render(request, 'payroll/my_payslips.html', {'payslips': payslips})


@login_required
def my_payslip_detail(request, pk):
    payslip = get_object_or_404(
        Payslip.objects.select_related('payroll_entry', 'payroll_entry__employee', 'payroll_entry__payroll_period'),
        pk=pk
    )

    if not hasattr(request.user, 'employee_profile'):
        return HttpResponseForbidden('You do not have an employee profile.')

    if payslip.payroll_entry.employee != request.user.employee_profile:
        return HttpResponseForbidden('You are not allowed to view this payslip.')

    return render(request, 'payroll/payslip_detail.html', {'payslip': payslip})


# -----------------------------
# Approval views
# -----------------------------

@login_required
@group_required('Finance Manager')
def approval_list(request):
    periods = PayrollPeriod.objects.all()
    return render(request, 'payroll/approval_list.html', {'periods': periods})


@login_required
@group_required('Finance Manager')
def approval_create(request, period_id):
    period = get_object_or_404(PayrollPeriod, pk=period_id)

    if request.method == 'POST':
        form = ApprovalForm(request.POST)
        if form.is_valid():
            approval = form.save(commit=False)
            approval.payroll_period = period
            approval.approved_by = request.user
            approval.save()

            # If approved, update the payroll period status
            if approval.status == 'Approved':
                period.status = 'Approved'
                period.save()

            messages.success(request, 'Approval recorded successfully.')
            return redirect('approval_list')
    else:
        form = ApprovalForm()

    return render(request, 'payroll/form.html', {'form': form, 'title': f'Approve {period.name}'})


# -----------------------------
# Summary view
# -----------------------------

@login_required
def payroll_summary(request):
    allowed = request.user.groups.filter(
        name__in=['Payroll Officer', 'Finance Manager']
    ).exists()

    if not allowed:
        return HttpResponseForbidden('You are not allowed to view the payroll summary.')

    periods = PayrollPeriod.objects.all()
    summary_rows = []

    for period in periods:
        entries = period.payroll_entries.all()

        total_basic = entries.aggregate(total=Sum('basic_pay'))['total'] or 0
        total_bonus = entries.aggregate(total=Sum('bonus_amount'))['total'] or 0
        total_tax = entries.aggregate(total=Sum('tax_amount'))['total'] or 0
        total_pension = entries.aggregate(total=Sum('pension_amount'))['total'] or 0
        total_other = entries.aggregate(total=Sum('other_deductions'))['total'] or 0
        total_net = entries.aggregate(total=Sum('net_pay'))['total'] or 0

        summary_rows.append({
            'period': period,
            'employee_count': entries.count(),
            'total_basic': total_basic,
            'total_bonus': total_bonus,
            'total_tax': total_tax,
            'total_pension': total_pension,
            'total_other': total_other,
            'total_net': total_net,
        })

    return render(request, 'payroll/payroll_summary.html', {'summary_rows': summary_rows})