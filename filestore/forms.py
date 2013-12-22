from django import forms

class FileUploadForm(forms.Form):
    plaintext_digest = forms.CharField(max_length = 512)
    plaintext_digest_algorithm = forms.CharField(max_length = 20)
    path = forms.CharField(max_length = 256)
    name = forms.CharField(max_length = 100)
    encrypted_content = forms.FileField()
