from django.db import models
from django.contrib.auth.models import User

class UserData(models.Model):
    user = models.ForeignKey(User, unique=True)
    public_key = models.BinaryField()

class EncryptedUserFile(models.Model):
    user = models.ForeignKey(User)
    encrypted_file = models.FileField(upload_to='encstore')

