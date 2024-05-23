# app/forms.py
from django import forms

class UserCreationForm(forms.Form):
    username = forms.CharField(max_length=100)
    name = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    age = forms.IntegerField()
    password = forms.CharField(widget=forms.PasswordInput)
    location = forms.CharField(max_length=100)
    sex = forms.CharField(max_length=10)
    mail = forms.EmailField()

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

