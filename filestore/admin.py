from django.contrib import admin
from filestore.models import UserData, EncryptedFileContent

admin.site.register(UserData)
admin.site.register(EncryptedFileContent)
