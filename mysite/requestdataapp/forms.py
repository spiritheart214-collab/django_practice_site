from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile


def validate_file_name(file: InMemoryUploadedFile) -> None:
    if file.name and "virus" in file.name:
        raise ValidationError("file name should not contain 'virus'")


class UserBioForm(forms.Form):
    name = forms.CharField(label="Full Name",
                           max_length=100,
                           widget=forms.TextInput(attrs={
                               "class": "form-input",
                               "id": "name-id",
                               "type": "text",
                               "placeholder": "Enter your full name",
                           }),
                           validators=[validate_file_name]
                           )

    age = forms.IntegerField(label="Age",
                             min_value=1,
                             max_value=99,
                             widget=forms.NumberInput(attrs={
                                 "class": "form-input",
                                 "placeholder": "Enter your age",
                             }))

    bio = forms.CharField(label="Biography",
                          widget=forms.Textarea(attrs={
                              "id": "bio",
                              "cols": "30",
                              "rows": "6",
                              "class": "form-textarea",
                              "placeholder": "Tell us about yourself...",

                          }))


class UploadFileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={
        "type": "file",
        "name": "my_file",
        "id": "fileInput",
        "class": "file-input"
    }))
