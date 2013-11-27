from django.shortcuts import render

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt

from filestore.models import PublicKeyFile, FileMetadata, EncryptedFileContent
from filestore.forms import FileUploadForm
from filestore.util import http_basic_auth, HttpStatus

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
        return HttpResponse(content="Object exists", status=HttpStatus.EXISTS)

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
    return HttpResponseRedirect(reverse('filestore:list_files'))
