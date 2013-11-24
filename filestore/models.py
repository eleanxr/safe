from django.db import models
from django.contrib.auth.models import User

import os

class UserData(models.Model):
    user = models.ForeignKey(User, unique=True)
    public_key = models.FileField(upload_to="public_keys")

class FileMetadata(models.Model):
    filename = models.CharField(max_length=100)

def choose_file_name(instance, filename):
    return os.path.join(
        'encstore', 
        instance.user.username,
        instance.metadata.filename
    )

class EncryptedFileContent(models.Model):
    user = models.ForeignKey(User)
    metadata = models.ForeignKey(FileMetadata)
    data_store = models.FileField(upload_to=choose_file_name)

