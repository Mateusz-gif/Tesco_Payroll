from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.urls import reverse
from datetime import date

from .models import Department, Employee, PayrollPeriod, PayrollEntry, Payslip


class PayrollModelTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Store', description='Store staff')
        self.user = User.objects.create_user(username='user1', password='password')

        self.employee = Employee.objects.create(
            user=self.user,
            department=self.department,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='123456',
            address='Dublin',
            hire_date=date(2025, 1, 1),
            job_title='Cashier',
            basic_salary=2500.00,
            is_active=True
        )

        self.period = PayrollPeriod.objects.create(
            name='January Payroll',
            month=1,
            year=2026,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            status='Draft'
        )

    def test_net_pay_is_calculated(self):
        entry = PayrollEntry.objects.create(
            employee=self.employee,
            payroll_period=self.period,
            basic_pay=2500.00,
            overtime_hours=5,
            overtime_amount=100.00,
            bonus_amount=50.00,
            tax_amount=300.00,
            pension_amount=100.00,
            other_deductions=50.00
        )
        self.assertEqual(float(entry.net_pay), 2200.00)


class PayrollViewTests(TestCase):
    def setUp(self):
        for group_name in ['HR Manager', 'Payroll Officer', 'Finance Manager', 'Employee']:
            Group.objects.create(name=group_name)

        self.department = Department.objects.create(name='Store', description='Store staff')

        self.hr_user = User.objects.create_user(username='hr1', password='password')
        self.hr_user.groups.add(Group.objects.get(name='HR Manager'))

        self.employee_user = User.objects.create_user(username='user1', password='password')
        self.employee_user.groups.add(Group.objects.get(name='Employee'))

        self.employee = Employee.objects.create(
            user=self.employee_user,
            department=self.department,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='123456',
            address='Dublin',
            hire_date=date(2025, 1, 1),
            job_title='Cashier',
            basic_salary=2500.00,
            is_active=True
        )

        self.period = PayrollPeriod.objects.create(
            name='January Payroll',
            month=1,
            year=2026,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            status='Draft'
        )

        self.entry = PayrollEntry.objects.create(
            employee=self.employee,
            payroll_period=self.period,
            basic_pay=2500.00,
            overtime_hours=5,
            overtime_amount=100.00,
            bonus_amount=50.00,
            tax_amount=300.00,
            pension_amount=100.00,
            other_deductions=50.00
        )

        self.payslip = Payslip.objects.create(
            payroll_entry=self.entry,
            issue_date=date(2026, 1, 31),
            reference_code='PS-2026-1-1'
        )

    def test_hr_can_open_employee_list(self):
        self.client.login(username='hr1', password='password')
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)

    def test_employee_can_view_own_payslip(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('my_payslip_detail', args=[self.payslip.pk]))
        self.assertEqual(response.status_code, 200)