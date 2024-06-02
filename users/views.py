from django.http import HttpResponse
from django.shortcuts import render

def users(request):
    #return HttpResponse("users test view.")
    return render(request, template_name="users/base_users.html")
