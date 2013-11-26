from django.db import models
from django.contrib.auth.models import User

import os

def key_file_location(instance, filename):
    return os.path.join('public_keys', instance.user.username, filename)

class PublicKeyFile(models.Model):
    """
    An object to hold a reference to a public key file.
    """
    key_file = models.FileField(upload_to=key_file_location)
    user = models.ForeignKey(User)

class FileMetadata(models.Model):
    digest = models.CharField(max_length=512) # 256 bytes in hex
    digest_algorithm = models.CharField(max_length=20)
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
    
    def __unicode__(self):
        return self.metadata.filename;

