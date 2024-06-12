from django.contrib import admin
from django.urls import path, re_path
from . import views

app_name = 'users'

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$|^\/$", views.users, name=app_name),
    path('artists/', views.ArtistsListView.as_view(), name="artists"),
    path('artists/<slug:slug>-<int:pk>/', views.ArtistDetailView.as_view(), name="artist_details"),
]