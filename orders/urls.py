from django.contrib import admin
from django.urls import path, re_path
from . import views

app_name = 'orders'

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$|^\/$", views.orders, name=app_name),
    path('checkout/', views.checkout, name="checkout"),
    path('process-payment/', views.process_payment, name='process-payment'),
]