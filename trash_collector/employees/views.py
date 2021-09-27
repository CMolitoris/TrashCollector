from trash_collector.customers.views import one_time_pickup, suspend_service
from django.http import HttpResponse
from django.shortcuts import render
from django.apps import apps
from customers.models import Customer
import datetime
from django.db.models import Q


# Create your views here.

# TODO: Create a function for each path created in employees/urls.py. Each will need a template as well.


def index(request):
    # This line will get the Customer model from the other app, it can now be used to query the db for Customers
    Customer = apps.get_model('customers.Customer')
    return render(request, 'employees/index.html')

def employee_todays_pickups(request):
    logged_in_employee = request.user
    # Filters customers down to matching employees zip code
    employee_pickup_list = Customer.objects.filter(zip_code = logged_in_employee.zip_code)
    # Gets the day of the week (Monday, Tuesday, ...)
    day_of_week = datetime.datetime.now()
    day_of_week = day_of_week.strftime("%A")

    #Gets current day in format yyyy-mm-dd
    current_day = datetime.date
    current_day = current_day.strftime("%Y-%m-%d")

    #Filters list to match either day of week or one time pick up on todays date
    employee_pickup_list = employee_pickup_list.filter(Q(weekly_pickup = day_of_week) | Q(one_time_pickup = current_day))

    #Filters list to exclude suspended accounts
    employee_pickup_list = employee_pickup_list.exclude(Q(suspend_start__lt = current_day) % Q(suspend_end__gte = current_day))

    #Filters list to exclude already picked up trash
    employee_pickup_list = employee_pickup_list.exclude(date_of_last_pickup = current_day)
