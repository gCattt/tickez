from django.http import HttpResponse
from django.shortcuts import render

def customers(request):
    #return HttpResponse("customers test view.")
    return render(request, template_name="customers/base_customers.html")
