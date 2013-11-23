from django.shortcuts import render

from django.http import HttpResponse

def user_key(request):
    return HttpResponse("User information or accept key.")
