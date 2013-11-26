from django.contrib import admin
from filestore.models import PublicKeyFile, EncryptedFileContent

admin.site.register(PublicKeyFile)
admin.site.register(EncryptedFileContent)
