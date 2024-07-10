from django.contrib import admin
from django.urls import path, re_path
from . import views

app_name = 'products'

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$|^\/$", views.products, name=app_name),
    path('events/', views.EventsListView.as_view(), name="events"),
    path('events/<slug:slug>-<int:pk>/', views.EventDetailView.as_view(), name="event-details"),

    path('create-event/', views.create_event, name="create-event"),
    path('update-event/<slug:slug>-<int:pk>/', views.UpdateEventView.as_view(), name="update-event"),
    path('delete-event/<slug:slug>-<int:pk>/', views.DeleteEventView.as_view(), name="delete-event"),

    path('create-ticket/<slug:event_slug>-<int:event_pk>/', views.create_ticket, name="create-ticket"),
    path('update-ticket/<slug:event_slug>-<int:event_pk>/<slug:ticket_slug>-<int:ticket_pk>/', views.UpdateTicketView.as_view(), name="update-ticket"),
    path('delete-ticket/<slug:event_slug>-<int:event_pk>/<slug:ticket_slug>-<int:ticket_pk>/', views.DeleteTicketView.as_view(), name="delete-ticket"),

    path('statistics/<slug:slug>-<int:pk>/', views.event_statistics, name="event-statistics"),
]