
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.apps import apps
from customers.models import Customer
import datetime
from django.db.models import Q
from django.urls.base import reverse
from .models import Employee


# Create your views here.

# TODO: Create a function for each path created in employees/urls.py. Each will need a template as well.

@login_required
def index(request):
    # This line will get the Customer model from the other app, it can now be used to query the db for Customers
    logged_in_user = request.user
    try:
        # This line will return the customer record of the logged-in user if one exists
        logged_in_employee = Employee.objects.get(user=logged_in_user)

        context = {
            "employee" : logged_in_employee
        }

        return HttpResponseRedirect(reverse('employees:home'))
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('employees:create'))
    

@login_required
def employee_todays_pickups(request):
    logged_in_employee = request.user
    logged_in_employee = Employee.objects.get(user_id = logged_in_employee)
    # Filters customers down to matching employees zip code
    employee_pickup_list = Customer.objects.filter(zip_code = logged_in_employee.zip_code)
    # Gets the day of the week (Monday, Tuesday, ...)
    day_of_week = datetime.datetime.now()
    day_of_week = day_of_week.strftime("%A")

    #Gets current day in format yyyy-mm-dd
    current_day = datetime.date.today()

    #Filters list to match either day of week or one time pick up on todays date
    employee_pickup_list = employee_pickup_list.filter(Q(weekly_pickup = day_of_week) | Q(one_time_pickup = current_day))

    #Gathers ONLY one-time pickup to refund (already paid)
    OT_pickup_list = employee_pickup_list.filter(one_time_pickup = current_day)

    #Filters list to exclude suspended accounts
    employee_pickup_list = employee_pickup_list.exclude(Q(suspend_start__lt = current_day) & Q(suspend_end__gte = current_day))

    #Filters list to exclude already picked up trash
    employee_pickup_list = employee_pickup_list.exclude(date_of_last_pickup = current_day)

    pickup_list_addresses = []
    for customer in employee_pickup_list:
        pickup_list_addresses.append(customer.address)
        

    context = {
        "pickup_list": employee_pickup_list,
        "employee": logged_in_employee,
        "OT_pickup_list": OT_pickup_list,
        "pickup_list_addresses":pickup_list_addresses
    }

    return render(request, 'employees/index.html', context)

@login_required
def create(request):
    logged_in_user = request.user
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        zip_from_form = request.POST.get('zip_code')
        new_employee = Employee(name=name_from_form,user=logged_in_user,zip_code=zip_from_form)
        new_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        return render(request, 'employees/create.html')

@login_required
def edit_profile(request):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        zip_from_form = request.POST.get('zip')
        logged_in_employee.name = name_from_form
        logged_in_employee.zip = zip_from_form
        logged_in_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        context = {
            'logged_in_employee':logged_in_employee
        }
        return render(request,'employees/edit_profile.html',context)

@login_required
def confirm(request,customer_id):
    customer_to_update = Customer.objects.get(pk=customer_id)
    if(customer_to_update.one_time_pickup!=datetime.date.today()):
        customer_to_update.balance += 20.00
    customer_to_update.date_of_last_pickup = datetime.date.today()
    customer_to_update.save()
    return HttpResponseRedirect(reverse('employees:home')) 

@login_required
def weekday_filter(request):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    if request.method == "POST":
        day_of_week_filter = request.POST.get('weekday')
        filter_results = Customer.objects.filter(weekly_pickup = day_of_week_filter)
        context = {
            'filter_results':filter_results,
            'day_of_week': day_of_week_filter,
            'logged_in_employee': logged_in_employee
        }
        return render(request,'employees/filter.html',context)
    else:
        context = {
            'logged_in_employee':logged_in_employee
        }
        return render(request,'employees/filter.html', context)
        
