from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UGCItem, Rating, Discussion, UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UGCItemForm(forms.ModelForm):
    class Meta:
        model = UGCItem
        fields = ['image', 'content']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['content']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_photo', 'bio']