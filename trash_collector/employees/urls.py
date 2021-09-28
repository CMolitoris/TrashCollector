
from django.urls import path
from . import views

# TODO: Determine what distinct pages are required for the user stories, add a path for each in urlpatterns

app_name = "employees"
urlpatterns = [
    path('', views.index, name="index"),
    path('employee/', views.employee_todays_pickups, name = "home"),
    path('new/',views.create,name='create'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('confirm/<int:customer_id>',views.confirm,name='confirm'),
    path('filter/', views.weekday_filter, name = "filter"),

]