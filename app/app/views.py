# app/views.py
from django.shortcuts import render, redirect
from .forms.forms import UserCreationForm, UserLoginForm
from .Class.User import User
from .utils import graphDB
import bcrypt
import re
from django.contrib import messages
from .Class.Post import Post
from django.core.files.storage import FileSystemStorage
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
            GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
            # Vérifier si le mot de passe est bien le bon
            username = form.cleaned_data['username']
            if not GDB.check_username_exists(username):
                return render(request, 'login.html', {'form': form, 'error': 'Invalid username or password'})
            password = form.cleaned_data['password']
            p = GDB.get_password_by_username(username)
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
    friends_requests = GDB.get_friends_requests(request.session['user']["username"])
    friends_posts = GDB.get_friends_posts(request.session['user']["username"])
    recommended_posts = GDB.get_recommendations_posts(request.session['user']["username"])
    sorted_friends_posts = sorted(friends_posts, key=lambda x: x['date'], reverse=True)
    sorted_recommended_posts = sorted(recommended_posts, key=lambda x: x['date'], reverse=True)

    if request.method == 'POST':
        search_query = request.POST.get('search_query', '')
        if search_query:
            return redirect('search_profil', username=search_query)
    return render(request,
                  'main_page.html',
                  {'friends': friends, 'friends_requests': friends_requests, 'friends_posts': sorted_friends_posts, 'recommended_posts': sorted_recommended_posts})

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
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    username = request.session['user']['username']
    posts = GDB.get_posts(username)
    friends = GDB.get_friends(username)
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image') if 'image' in request.FILES else None
        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            uploaded_file_url = fs.url(filename)
        else:
            uploaded_file_url = None

        new_post = Post(content, uploaded_file_url)
        GDB.add_post(username, new_post)
        return redirect('profil')

    return render(request, 'profil.html', {'posts': posts, 'friends': friends})

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

def search_profil(request, username=None):
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
                posts = GDB.get_posts(username)
                is_friend = GDB.is_friend(request.session['user']['username'], username)
                is_friend_request = GDB.has_send_friend_request(request.session['user']['username'], username)
                show_button = not (is_friend or is_friend_request)
                return render(request, 'search_profil.html', {"username":username,"name": name, "surname": surname, "age": age ,
                                                  "location": location, "sex": sex, "mail": mail, "posts": posts, "show_button": show_button})
            else:
                messages.error(request, f"User '{search_query}' not found.")
                return redirect('search_profil')
    return render(request, 'main_page.html')

def visit_profil(request, username):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    user_info = GDB.get_user_by_username(username)
    name = user_info["name"]
    surname = user_info["surname"]
    age = user_info["age"]
    location = user_info["location"]
    sex = user_info["sex"]
    mail = user_info["mail"]
    posts = GDB.get_posts(username)
    is_friend = GDB.is_friend(request.session['user']['username'], username)
    is_friend_request = GDB.has_send_friend_request(request.session['user']['username'], username)
    show_button = not (is_friend or is_friend_request)
    return render(request, 'search_profil.html', {"username": username, "name": name, "surname": surname, "age": age,
                                                  "location": location, "sex": sex, "mail": mail, "posts": posts,
                                                  "show_button": show_button})
def send_friend_request(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    sender = request.session['user']['username']
    receiver = request.POST['to_user']
    GDB.add_new_friend_request(sender, receiver)
    return redirect('search_profil')

def accept_friend_request(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    sender = request.POST['friend_name']
    receiver = request.session['user']['username']
    GDB.accept_friend_request(sender, receiver)
    return redirect('main_page')

def private_messages_list(request):
    username = request.session['user']['username']
    print(username)
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    if username:
        friends = GDB.get_friends(username)
        return render(request, 'private_message_list.html', {'friends': friends})
    else:
        return render(request, 'login.html')

def private_messages(request):
    username = request.session['user']['username']
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    if request.method == 'POST':
        friend_username = request.POST.get('friend_name')
        content_message = request.POST.get('send_message')
        if content_message:
            friend_username = request.POST.get('friend_name')
            GDB.create_message(username,friend_username, content_message)
            messages = GDB.get_messages(username, friend_username)
            print(friend_username)
            print(messages)
            return render(request, 'private_message.html', {'friend_username': friend_username, 'messages': messages})

        if friend_username:
            if(GDB.check_discussion(username, friend_username)):
                messages = GDB.get_messages(username, friend_username)
                return render(request, 'private_message.html', {'friend_username': friend_username, 'messages': messages})
            else:
                GDB.create_discussion(username, friend_username)
                return render(request, 'private_message.html', {'friend_username': friend_username})
    return render(request, 'private_message.html')