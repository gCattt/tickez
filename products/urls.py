from django.contrib import admin
from django.urls import path, re_path
from . import views

app_name = 'products'

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$|^\/$", views.products, name=app_name),
    path('events/', views.EventsListView.as_view(), name="events"),
    path('events/<slug:slug>-<int:pk>/', views.EventDetailView.as_view(), name="event_details"),
]