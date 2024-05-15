from django.contrib import admin
from django.urls import path, re_path
from . import views

app_name = 'customers'

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$|^\/$", views.customers, name=app_name),
]