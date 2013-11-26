from django import forms

class FileUploadForm(forms.Form):
    digest = forms.CharField(max_length = 512)
    digest_algorithm = forms.CharField(max_length = 20)
    encrypted_content = forms.FileField()
