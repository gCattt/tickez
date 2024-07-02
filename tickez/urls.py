"""
URL configuration for tickez project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.urls import path, re_path, include

from . import views
from django.views.generic.base import RedirectView

from .initcmds import *


urlpatterns = [
    path('admin/', admin.site.urls),

    path('favicon.ico', RedirectView.as_view(url='/static/images/icons/favicon.ico', permanent=True)),
    re_path(r"^$|^\/$|^home\/$", views.home_page, name='homepage'),

    path('common/', include('common.urls')),
    path('users/', include('users.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),

    #path('register/', views.UserCreateView.as_view(), name='register-customer'),
    #path('register_organizer/', views.OrganizerCreateView.as_view(), name='register-organizer'),
    path('login/', views.login_user, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

#erase_db()
init_db()

admin.site.site_header = "Tickez Administration Page"
admin.site.site_title = "Tickez"
admin.site.index_title = "Admin Area"