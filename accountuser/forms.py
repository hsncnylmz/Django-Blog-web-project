from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'cover_photo', 'birth_date', 'location', 'website', 'twitter', 'github', 'linkedin', 'instagram', 'interests', 'education', 'job']

# Diğer form class'larını ekleyebilirsiniz
