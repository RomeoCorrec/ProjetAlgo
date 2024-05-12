from django import forms

class UserRegistrationForm(forms.Form):
    username = forms.CharField(label='Nom d\'utilisateur', max_length=100)
    name = forms.CharField(label='Prénom', max_length=100)
    surname = forms.CharField(label='Nom de famille', max_length=100)
    age = forms.IntegerField(label='Âge')
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    location = forms.CharField(label='Localisation', max_length=100)
    sex = forms.ChoiceField(label='Sexe', choices=[('M', 'Masculin'), ('F', 'Féminin')])
    mail = forms.EmailField(label='Adresse email')