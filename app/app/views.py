# app/views.py
from django.shortcuts import render, redirect
from .forms.forms import UserCreationForm, UserLoginForm
from .User import User
from .utils import graphDB
import bcrypt

def create_account(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
            # Traitez les données du formulaire ici (par exemple, enregistrer l'utilisateur dans la base de données)
            # Exemple simplifié :
            username = form.cleaned_data['username']
            # Vérifier si l'utilisateur existe déjà
            if GDB.check_username_exists(username):
                return render(request, 'create_account.html', {'form': form, 'error': 'Username already exists'})
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            age = form.cleaned_data['age']
            hpassword = hash_password(form.cleaned_data['password'])
            location = form.cleaned_data['location']
            sex = form.cleaned_data['sex']
            mail = form.cleaned_data['mail']
            # Ici, vous pouvez créer un objet User ou faire d'autres opérations nécessaires
            user = User(username, name, surname, age, hpassword, location, sex, mail)
            GDB.add_new_user(user)

            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'create_account.html', {'form': form})

def index(request):
    return redirect('create_account')

def home(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            # Vérifier si le mot de passe est bien le bon
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(password)
            GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
            p = GDB.get_password_by_username(username)
            print(p)
            if check_password(password, p):
                return redirect('main_page', username = username)
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid username or password'})
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def main_page(request, username):
    return render(request, 'main_page.html', {'username': username})

def deconexion(request):
    return render(request, 'index.html')

def hash_password(password: str) -> str:
    # Génère un sel aléatoire
    salt = bcrypt.gensalt()

    # Hache le mot de passe avec le sel
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Retourne le mot de passe haché sous forme de chaîne
    return hashed_password.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def profil(request, username):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    user_info = GDB.get_user_by_username(username)
    return render(request, 'profil.html', {'username': username, 'user_info': user_info})