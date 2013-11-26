from django.shortcuts import render

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt

from filestore.models import PublicKeyFile, FileMetadata, EncryptedFileContent
from filestore.forms import FileUploadForm

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
            return HttpResponseRedirect(reverse('filestore:list_files'))
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
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            return __handle_upload(request)
    else:
        form = FileUploadForm()
    return render(request, 'filestore/upload.html', {
        'form': form
    }) 

def __handle_upload(request):
    filename = request.FILES['encrypted_content'].name
    digest = request.POST['digest']
    digest_algorithm = request.POST['digest_algorithm']
    
    file_exists = FileMetadata.objects.filter(
        digest_algorithm=digest_algorithm,
        digest=digest
    )

    # If we already have an entry for that digest, don't replicate it
    if file_exists:
        return HttpResponse(content="Object exists", status_code=302)

    # A file of that digest/algorithm combination doesn't exist.
    metadata = FileMetadata(
        filename=filename,
        digest=digest,
        digest_algorithm=digest_algorithm
    )

    metadata.save()
    
    data = EncryptedFileContent(
        user=request.user,
        metadata=metadata,
        data_store=request.FILES['encrypted_content']
    )
    data.save()
    return HttpResponse('Data uploaded')
