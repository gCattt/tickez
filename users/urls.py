from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.urls import path, re_path

from . import views

app_name = 'users'

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$|^\/$", views.users, name=app_name),

    path('register/', views.CustomerCreateView.as_view(), name='register-customer'),
    path('register-organizer/', views.OrganizerCreateView.as_view(), name='register-organizer'),
    path('login/', views.login_user, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('admin-profile/', views.AdminProfileView.as_view(), name="admin-profile"),
    path('profile/', views.ProfileView.as_view(), name="profile"),

    path('toggle-follow/<str:entity_type>/<int:entity_pk>/', views.toggle_follow, name='toggle-follow'),

    path('artists/', views.ArtistsListView.as_view(), name="artists"),
    path('artists/<slug:slug>-<int:pk>/', views.ArtistDetailView.as_view(), name="artist-details"),
]