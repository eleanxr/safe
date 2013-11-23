from django.contrib import admin
from filestore.models import UserData, EncryptedUserFile

admin.site.register(UserData)
admin.site.register(EncryptedUserFile)
