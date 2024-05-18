from django.http import HttpResponse
from django.shortcuts import render

def sellers(request):
    #return HttpResponse("sellers test view.")
    return render(request, template_name="sellers/base_sellers.html")