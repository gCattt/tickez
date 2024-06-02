from django.http import HttpResponse
from django.shortcuts import render

def products(request):
    #return HttpResponse("products test view.")
    return render(request, template_name="products/base_products.html")