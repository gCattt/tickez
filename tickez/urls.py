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

from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.conf import settings

from . import views
from django.views.generic.base import RedirectView


# definizione degli URL patterns per l'applicazione + aggiunta URL per servire file statici e media in fase di sviluppo
urlpatterns = [
    path('admin/', admin.site.urls),

    path('favicon.ico', RedirectView.as_view(url='/static/images/icons/favicon.ico', permanent=True)),
    re_path(r"^$|^\/$|^home\/$", views.home_page, name='homepage'),

    path('common/', include('common.urls')),
    path('users/', include('users.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),

    re_path(r"^404/$", views.custom_404_view, name="404"),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# personalizzazione dei titoli dell'area di amministrazione
admin.site.site_header = "Tickez Administration Page"
admin.site.site_title = "Tickez"
admin.site.index_title = "Admin Area"