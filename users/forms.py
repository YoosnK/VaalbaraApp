from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    photo = forms.ImageField(
        label="Ảnh đại diện",
        required=False,
        widget=forms.FileInput(attrs={'class':'form-fileinput'})
    )
    email = forms.EmailField(
        label="Email*",
        required=True,
        widget=forms.TextInput(attrs={'class':'form-textinput'})
    )
    first_name = forms.CharField(
        label="Tên",
        required=False,
        widget=forms.TextInput(attrs={'class':'form-textinput'})
    )
    last_name = forms.CharField(
        label="Họ",
        required=False,
        widget=forms.TextInput(attrs={'class':'form-textinput'})
    )
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # Ensure these match the fields in your admin.py add_fieldsets
        fields = ('username', 'first_name', 'last_name', 'email', 'photo', 'age')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields