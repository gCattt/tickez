from django.contrib import admin
from django.urls import path, re_path
from . import views

app_name = 'common'

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$|^\/$", views.common, name=app_name),
    path('events/', views.EventListView.as_view(), name="events"),
]