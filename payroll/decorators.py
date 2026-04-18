from django.contrib.auth.decorators import user_passes_test


# This checks whether the user is in a named Django group
def group_required(group_name):
    return user_passes_test(lambda u: u.is_authenticated and u.groups.filter(name=group_name).exists())


# These simple helper functions can be used later if needed
def is_hr(user):
    return user.is_authenticated and user.groups.filter(name='HR Manager').exists()


def is_payroll_officer(user):
    return user.is_authenticated and user.groups.filter(name='Payroll Officer').exists()


def is_finance_manager(user):
    return user.is_authenticated and user.groups.filter(name='Finance Manager').exists()


def is_employee(user):
    return user.is_authenticated and user.groups.filter(name='Employee').exists()