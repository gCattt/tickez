from django.contrib import admin
from django.urls import path, re_path
from . import views

app_name = 'common'

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$|^\/$", views.common, name=app_name),
    path('venues/', views.VenuesListView.as_view(), name="venues"),
    path('venues/<slug:slug>-<int:pk>/', views.VenueDetailView.as_view(), name="venue-details"),
    path('search/', views.search_results, name="search-results"),
]