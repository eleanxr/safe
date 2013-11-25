from django.shortcuts import render

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt

from filestore.models import UserData, FileMetadata, EncryptedFileContent

from functools import wraps

def http_basic_auth(func):
    """
    A decorator to allow authentication to be performed
    on a method decorated with @login_required using the
    HTTP Authorization header.

    This has to be a decorator because it must be applied
    *before* the @login_required decorator is applied,
    otherwise @login_required's redirect would kick in
    before we have an opportunity to read the header.
    Such behavior would keep this method from being used
    as a service method.
    """
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        from django.contrib.auth import authenticate, login
        if request.META.has_key('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if authmeth.lower() == 'basic':
                auth = auth.strip().decode('base64')
                username, password = auth.split(':', 1)
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
        return func(request, *args, **kwargs)
    return _decorator

def loginpage(request):
    return render(request, 'filestore/login.html', {})

def do_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('filestore:userinfo'))
        else:
            return HttpResponse("User %s is not active" % user)
    else:
        return HttpResponse("Invalid username or password")

@login_required
def list_files(request):
    file_list = EncryptedFileContent.objects.filter(user=request.user)
    context = {
        'user': request.user,
        'file_list': file_list,
        }
    return render(request, 'filestore/filelist.html', context)

@login_required
def userinfo(request):
    return HttpResponse("Information for user %s" % request.user)

@http_basic_auth
@login_required
def addkey(request):
    if request.method == 'POST' and request.FILES:
        keyfile = request.FILES['key']
        if keyfile:
            handle_key_upload(request.user, keyfile)
    else:
        return HttpResponse("Only accepts posts")

def handle_key_upload(user, keyfile):
    userdata = UserData(user_id=user.id, public_key=keyfile)
    userdata.save()

@http_basic_auth
@login_required
@csrf_exempt # Probably not a great idea, but here for now.
def upload_file(request):
    if request.method == 'POST':
        filename = request.POST['filename']
        metadata = FileMetadata(filename=filename)
        metadata.save()
        data = EncryptedFileContent(
            user=request.user,
            metadata=metadata,
            data_store=request.FILES['file']
        )
        data.save()
        return HttpResponse('Data uploaded')
    else:
        return HttpResponse('This method accepts only POST data')
