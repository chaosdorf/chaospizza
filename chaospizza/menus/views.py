# pylint: disable=C0111
# from django.shortcuts import render
from django.http import HttpResponse


def menu_home(request):
    """Django view which returns simple hello world text."""
    print(request)
    return HttpResponse("hi from menus app")
