from django.db import models
from django.contrib.auth.models import User

import os

#
# Public Key Storage
#

def key_file_location(instance, filename):
    return os.path.join('public_keys', instance.user.username, filename)

class PublicKeyFile(models.Model):
    """
    An object to hold a reference to a public key file.
    """
    key_file = models.FileField(upload_to=key_file_location)
    user = models.ForeignKey(User)

#
# File Storage
#

class FileMetadata(models.Model):
    """
    Contains metadata for a file, including a digest of the cleartext
    file and a name for the file.
    """
    plaintext_digest = models.CharField(max_length=512) # 256 bytes in hex
    plaintext_digest_algorithm = models.CharField(max_length=20)
    
    def __unicode__(self):
        return "%s" % self.plaintext_digest

def choose_file_name(instance, filename):
    return os.path.join(
        'data', 
        instance.user.username,
        instance.metadata.plaintext_digest
    )

class EncryptedFileContent(models.Model):
    """
    Contains information about encrypted content for a user.
    """
    user = models.ForeignKey(User)
    # There can be many encrypted versions of a single logical file.
    metadata = models.ForeignKey(FileMetadata)
    data = models.FileField(upload_to=choose_file_name)
    
    def __unicode__(self):
        return "Encrypted file with digest %s" % self.encrypted_digest;

PATH_LENGTH = 256

class StoredFile(models.Model):
    user = models.ForeignKey(User)
    metadata = models.ForeignKey(FileMetadata)
    encrypted_content = models.ForeignKey(EncryptedFileContent)
    path = models.CharField(max_length=PATH_LENGTH)
    filename = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.path
    
    class Meta:
        ordering = ('path', 'filename')
