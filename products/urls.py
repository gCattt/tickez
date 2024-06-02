from django.contrib import admin
from django.urls import path, re_path
from . import views

app_name = 'products'

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$|^\/$", views.products, name=app_name),
]