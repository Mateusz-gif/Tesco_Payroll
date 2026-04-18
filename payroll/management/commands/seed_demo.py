from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from payroll.models import Department, Employee, PayrollPeriod, PayrollEntry, Payslip


class Command(BaseCommand):
    help = 'Create demo groups, users, and sample payroll data'

    def handle(self, *args, **kwargs):
        # Create groups
        group_names = ['HR Manager', 'Payroll Officer', 'Finance Manager', 'Employee']
        for name in group_names:
            Group.objects.get_or_create(name=name)

        # Create users with password "password"
        admin_user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@admin.com'})
        if created:
            admin_user.set_password('password')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()

        hr_user, created = User.objects.get_or_create(username='hr1', defaults={'email': 'hr1@tesco.com'})
        if created:
            hr_user.set_password('password')
            hr_user.save()
        hr_user.groups.add(Group.objects.get(name='HR Manager'))

        payroll_user, created = User.objects.get_or_create(username='payroll1', defaults={'email': 'payroll1@tesco.com'})
        if created:
            payroll_user.set_password('password')
            payroll_user.save()
        payroll_user.groups.add(Group.objects.get(name='Payroll Officer'))

        manager_user, created = User.objects.get_or_create(username='manager1', defaults={'email': 'manager1@tesco.com'})
        if created:
            manager_user.set_password('password')
            manager_user.save()
        manager_user.groups.add(Group.objects.get(name='Finance Manager'))

        employee_user, created = User.objects.get_or_create(username='user1', defaults={'email': 'user1@user1.com'})
        if created:
            employee_user.set_password('password')
            employee_user.save()
        employee_user.groups.add(Group.objects.get(name='Employee'))

        # Create departments
        store, _ = Department.objects.get_or_create(name='Store', defaults={'description': 'Tesco store employees'})
        warehouse, _ = Department.objects.get_or_create(name='Warehouse', defaults={'description': 'Tesco warehouse staff'})
        office, _ = Department.objects.get_or_create(name='Head Office', defaults={'description': 'Tesco office staff'})

        # Create employee profile for user1
        employee, _ = Employee.objects.get_or_create(
            user=employee_user,
            defaults={
                'department': store,
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'user1@user1.com',
                'phone': '123456789',
                'address': 'Dublin, Ireland',
                'hire_date': date(2025, 9, 1),
                'job_title': 'Cashier',
                'basic_salary': 2400.00,
                'is_active': True,
            }
        )

        # Create payroll period
        period, _ = PayrollPeriod.objects.get_or_create(
            name='March 2026 Payroll',
            month=3,
            year=2026,
            defaults={
                'start_date': date(2026, 3, 1),
                'end_date': date(2026, 3, 31),
                'status': 'Draft',
            }
        )

        # Create payroll entry
        entry, _ = PayrollEntry.objects.get_or_create(
            employee=employee,
            payroll_period=period,
            defaults={
                'basic_pay': 2400.00,
                'overtime_hours': 8,
                'overtime_amount': 120.00,
                'bonus_amount': 80.00,
                'tax_amount': 250.00,
                'pension_amount': 100.00,
                'other_deductions': 20.00,
            }
        )

        # Create payslip
        Payslip.objects.get_or_create(
            payroll_entry=entry,
            defaults={
                'issue_date': date(2026, 3, 31),
                'reference_code': f'PS-{period.year}-{period.month}-{entry.pk}'
            }
        )

        self.stdout.write(self.style.SUCCESS('Demo data created successfully.'))