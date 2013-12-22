from django.shortcuts import render

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.core.files import File

from django.db.models.fields.files import FieldFile

from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt

from filestore.models import PublicKeyFile, FileMetadata, EncryptedFileContent, StoredFile
from filestore.forms import FileUploadForm
from filestore.util import http_basic_auth, HttpStatus, digest_file

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
    file_list = StoredFile.objects.filter(user=request.user)
    # Build a list with the important information.
    files = []
    for item in file_list:
        files.append({
            'path': '%s/%s' % (item.path, item.filename),
            'plaintext_digest': item.metadata.plaintext_digest,
            'download_url': item.encrypted_content.data.url,
        })
    context = {
        'user': request.user,
        'files': files,
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
    plaintext_digest = request.POST['plaintext_digest']
    plaintext_digest_algorithm = request.POST['plaintext_digest_algorithm']
    path = request.POST['path']
    name = request.POST['name']
    
    # Look for existing metadata
    try:
        metadata = FileMetadata.objects.get(
            plaintext_digest_algorithm=plaintext_digest_algorithm,
            plaintext_digest=plaintext_digest
        )
    except FileMetadata.DoesNotExist:
        # Create a new one and save it
        metadata = FileMetadata(
            plaintext_digest = plaintext_digest,
            plaintext_digest_algorithm = plaintext_digest_algorithm
        )
        metadata.save()

    try:
        stored_data = EncryptedFileContent.objects.get(metadata = metadata, user = request.user)
    except EncryptedFileContent.DoesNotExist:
        stored_data = EncryptedFileContent(
            user = request.user,
            metadata = metadata,
            data = request.FILES['encrypted_content']
        )
        stored_data.save()
    
    new_file = StoredFile(
        user = request.user,
        metadata = metadata,
        encrypted_content = stored_data,
        path = path,
        filename = name
    )
    
    new_file.save()
    
    return HttpResponseRedirect(reverse('filestore:list_files'))
