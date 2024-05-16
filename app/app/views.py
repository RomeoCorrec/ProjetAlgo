# app/views.py
from django.shortcuts import render, redirect
from .forms.creationAccount import UserCreationForm

def create_account(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Traitez les données du formulaire ici (par exemple, enregistrer l'utilisateur dans la base de données)
            # Exemple simplifié :
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            age = form.cleaned_data['age']
            password = form.cleaned_data['password']
            location = form.cleaned_data['location']
            sex = form.cleaned_data['sex']
            mail = form.cleaned_data['mail']
            # Ici, vous pouvez créer un objet User ou faire d'autres opérations nécessaires
            return render(request, 'account_created.html', {'username': username})
    else:
        form = UserCreationForm()
    return render(request, 'create_account.html', {'form': form})

def index(request):
    return redirect('create_account')

def home(request):
    return render(request, 'index.html')
def login_view(request):
    return render(request, 'login.html')