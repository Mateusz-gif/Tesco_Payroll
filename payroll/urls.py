from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Login and logout
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Employee pages
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_update'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('my-profile/', views.my_profile, name='my_profile'),

    # Payroll period pages
    path('periods/', views.payroll_period_list, name='payroll_period_list'),
    path('periods/add/', views.payroll_period_create, name='payroll_period_create'),
    path('periods/<int:pk>/edit/', views.payroll_period_update, name='payroll_period_update'),

    # Payroll entry pages
    path('entries/', views.payroll_entry_list, name='payroll_entry_list'),
    path('entries/add/', views.payroll_entry_create, name='payroll_entry_create'),
    path('entries/<int:pk>/', views.payroll_entry_detail, name='payroll_entry_detail'),

    # Payslip pages
    path('my-payslips/', views.my_payslips, name='my_payslips'),
    path('my-payslips/<int:pk>/', views.my_payslip_detail, name='my_payslip_detail'),

    # Approval pages
    path('approvals/', views.approval_list, name='approval_list'),
    path('approvals/<int:period_id>/add/', views.approval_create, name='approval_create'),

    # Summary page
    path('summary/', views.payroll_summary, name='payroll_summary'),
]