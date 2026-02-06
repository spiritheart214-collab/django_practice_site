from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "avatar",

        widgets = {
            'avatar': forms.FileInput(attrs={
                'accept': 'image/*',
                'onchange': 'previewAvatar(event)',
                'class': 'form-control',
                'id': 'avatar-input'
            })
        }