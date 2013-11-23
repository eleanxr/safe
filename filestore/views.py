from django.shortcuts import render

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect

def login(request):
    return render(request, 'filestore/login.html', {})

def do_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user:
        if user.is_active:
            login(request)
            return HttpResponseRedirect(reverse('filestore:userinfo'))
        else:
            return HttpResponse("User %s is not active" % user)
    else:
        return HttpResponse("Invalid username or password")

@login_required
def user_key(request):
    return HttpResponse("Information for user %s" % request.user)
