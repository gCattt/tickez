from django.http import HttpResponse
from django.shortcuts import render

def home_page(request):
    #return HttpResponse("Hello world! Questa è la home page.")
    return render(request, template_name="base.html")