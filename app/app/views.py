# app/views.py
from django.shortcuts import render, redirect
from .forms.forms import UserCreationForm, UserLoginForm
from .Class.User import User
from .utils import graphDB
import bcrypt
import re
from django.contrib import messages

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
            if not is_valid_password(form.cleaned_data['password']):
                return render(request, 'create_account.html', {'form': form, 'error': 'Invalid password'})
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            age = form.cleaned_data['age']
            hpassword = hash_password(form.cleaned_data['password'])
            location = form.cleaned_data['location']
            sex = form.cleaned_data['sex']
            print(sex)
            mail = form.cleaned_data['mail']
            print(mail)
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
            GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
            # Vérifier si le mot de passe est bien le bon
            username = form.cleaned_data['username']
            if not GDB.check_username_exists(username):
                return render(request, 'login.html', {'form': form, 'error': 'Invalid username or password'})
            password = form.cleaned_data['password']
            print(password)
            p = GDB.get_password_by_username(username)
            print(p)
            if check_password(password, p):
                user = GDB.get_user_by_username(username)
                request.session['user'] = user
                return redirect('main_page')
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid username or password'})
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def main_page(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    # Récupérer les amis de l'utilisateur
    friends = GDB.get_connected_users(request.session['user']["username"])
    print(friends)
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '')
        if search_query:
            return redirect('search_profil', username=search_query)
    return render(request, 'main_page.html')

def deconexion(request):
    request.session.flush()
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

def is_valid_password(password: str) -> bool:
    if len(password) < 9:
        return False

    has_uppercase = re.search(r'[A-Z]', password)
    has_digit = re.search(r'[0-9]', password)
    has_special_char = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)

    if not (has_uppercase and has_digit and has_special_char):
        return False

    return True

def profil(request):
    return render(request, 'profil.html')

def modify_profil(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    username = request.session['user']['username']
    user_info = GDB.get_user_by_username(username)
    name = user_info["name"]
    surname = user_info["surname"]
    age = user_info["age"]
    location = user_info["location"]
    sex = user_info["sex"]
    mail = user_info["mail"]
    if request.method == 'POST':
        user_info["name"] = request.POST['name']
        user_info["surname"] = request.POST['surname']
        user_info["age"] = request.POST['age']
        user_info["location"] = request.POST['location']
        user_info["sex"] = request.POST['sex']
        user_info["mail"] = request.POST['mail']

        GDB.modify_profil(username, user_info["name"], user_info["surname"], user_info["age"], user_info["location"],
                          user_info["sex"], user_info["mail"])
        modified_user = GDB.get_user_by_username(username)
        request.session['user'] = modified_user
        return redirect('profil')

    return render(request, 'modify_profil.html', {"name": name, "surname": surname, "age": age ,
                                                  "location": location, "sex": sex, "mail": mail})

def search_profil(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '')
        GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
        if search_query:
            username = search_query
            if GDB.check_username_exists(username):
                user_info = GDB.get_user_by_username(username)
                name = user_info["name"]
                surname = user_info["surname"]
                age = user_info["age"]
                location = user_info["location"]
                sex = user_info["sex"]
                mail = user_info["mail"]
                return render(request, 'search_profil.html', {"username":username,"name": name, "surname": surname, "age": age ,
                                                  "location": location, "sex": sex, "mail": mail})
            else:
                messages.error(request, f"User '{search_query}' not found.")
                return redirect('main_page')
    return render(request, 'main_page.html')