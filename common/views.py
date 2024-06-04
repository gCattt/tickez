from typing import Any
from django.http import HttpResponse
from django.shortcuts import render


def common(request):
    #return HttpResponse("common test view.")
    return render(request, template_name="common/base_common.html")
