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

def main_page(request, filter=""):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    username = request.session['user']['username']
    # Récupérer les amis de l'utilisateur
    friends = GDB.get_connected_users(username)
    recommendations = GDB.get_recommendations(username)
    friends_requests = GDB.get_friends_requests(username)
    if filter != "":
        friends_posts = GDB.get_filtered_friends_posts(username, filter)
    else:
        friends_posts = GDB.get_friends_posts(username)
    recommended_posts = GDB.get_recommendations_posts(username)
    sorted_friends_posts = sorted(friends_posts, key=lambda x: x['date'], reverse=True)
    sorted_recommended_posts = sorted(recommended_posts, key=lambda x: x['date'], reverse=True)
    post_id = []
    post_likes = []
    for post in sorted_friends_posts:
        post_id.append(post["id"])
        post_likes.append(GDB.get_like_count(int(post["id"])))
    friends_posts_with_ids = zip(sorted_friends_posts, post_id, post_likes)
    post_id_reco = []
    post_likes_reco = []
    for post in sorted_recommended_posts:
        post_id_reco.append(post["id"])
        post_likes_reco.append(GDB.get_like_count(int(post["id"])))
    sorted_recommended_posts = zip(sorted_recommended_posts, post_id_reco, post_likes_reco)
    has_new_notification = GDB.has_unseen_notification(username)
    return render(request,
                  'main_page.html',
                  {'friends': friends, 'friends_requests': friends_requests, 'friends_posts': friends_posts_with_ids,
                   'recommended_posts': sorted_recommended_posts, 'post_id': post_id, 'recommendations': recommendations,'has_new_notification':has_new_notification})

def like_post(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    username = request.session['user']['username']
    if request.method == 'POST':
        like_post_id = request.POST.get("like_post_id")
        if like_post_id:
            if not GDB.has_liked_post(int(like_post_id), username):
                GDB.like_post(int(like_post_id), username)
                post_author = GDB.get_post_by_id(int(like_post_id))["author"]
                content = f"{username} liked your post."
                GDB.create_notification(post_author, "like", content)
    return redirect('main_page')

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

def profil_page(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    username = request.session['user']['username']
    posts = GDB.get_posts(username)
    friends = GDB.get_friends(username)
    post_id = []
    post_likes = []
    for post in posts:
        post_id.append(post["id"])
        post_likes.append(GDB.get_like_count(int(post["id"])))
    posts = zip(posts, post_id, post_likes)
    return render(request, 'profil.html', {'posts': posts, 'friends': friends})

def delete_post(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    if request.method == 'POST':
        delete_post_id = request.POST.get("delete_post_id")
        print("POST_ID: ",delete_post_id)
        if delete_post_id:
            GDB.delete_post(int(delete_post_id))

    return redirect("profil_page")


# def post(request):
#     GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
#     username = request.session['user']['username']
#     if request.method == 'POST':
#         content = request.POST.get('content')
#         image = request.FILES.get('image') if 'image' in request.FILES else None
#         print("IMAGE:", image)
#         if image:
#             fs = FileSystemStorage('app/static/')
#             filename = fs.save(image.name, image)
#             uploaded_file_url = image.name
#         else:
#             uploaded_file_url = None
#
#         new_post = Post(content, uploaded_file_url)
#         GDB.add_post(username, new_post)
#     return redirect('profil_page')
def post(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    username = request.session['user']['username']
    if request.method == 'POST':
        content = request.POST.get('content')
        media = request.FILES.get('media')
        print("MEDIA:", media)
        if media:
            fs = FileSystemStorage('app/static/')
            filename = fs.save(media.name, media)
            uploaded_file_url = media.name
            if media.content_type.startswith('image/'):
                media_type = "image"
            elif media.content_type.startswith('video/'):
                media_type = "video"
            else:
                # Gérer les types de fichiers non pris en charge
                pass
        else:
            uploaded_file_url = None
            media_type = None
        new_post = Post(content, uploaded_file_url, media_type)
        GDB.add_post(username, new_post)
    return redirect('profil_page')

def modify_profil_page(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    username = request.session['user']['username']
    user_info = GDB.get_user_by_username(username)
    name = user_info["name"]
    surname = user_info["surname"]
    age = user_info["age"]
    location = user_info["location"]
    sex = user_info["sex"]
    mail = user_info["mail"]
    return render(request, 'modify_profil.html', {"name": name, "surname": surname, "age": age ,
                                                  "location": location, "sex": sex, "mail": mail})

def modify_profil(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    username = request.session['user']['username']
    user_info = GDB.get_user_by_username(username)
    if request.method == 'POST':
        user_info["name"] = request.POST['name']
        user_info["surname"] = request.POST['surname']
        user_info["age"] = request.POST['age']
        user_info["location"] = request.POST['location']
        user_info["sex"] = request.POST['sex']
        user_info["mail"] = request.POST['mail']
        user_info["private"] = request.POST['private']
        GDB.modify_profil(username, user_info["name"], user_info["surname"], user_info["age"], user_info["location"],
                          user_info["sex"], user_info["mail"], user_info["private"])
        modified_user = GDB.get_user_by_username(username)
        request.session['user'] = modified_user
    return redirect('profil_page')

def search_profil(request, username=None):
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '')
        GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
        if search_query:
            username = search_query
            if GDB.check_username_exists(username):
                if username == request.session['user']['username']:
                    return redirect('profil_page')
                is_friend = GDB.is_friend(request.session['user']['username'], username)
                is_friend_request = GDB.has_send_friend_request(request.session['user']['username'], username)
                if GDB.is_private(username) and not is_friend:
                    show_button = not (is_friend or is_friend_request)
                    return render(request, 'search_profil.html', {'username': username, 'private': True, 'show_button': show_button, 'is_friend': is_friend})
                show_button = not (is_friend or is_friend_request)
                user_info = GDB.get_user_by_username(username)
                friends = GDB.get_friends(username)
                name = user_info["name"]
                surname = user_info["surname"]
                age = user_info["age"]
                location = user_info["location"]
                sex = user_info["sex"]
                mail = user_info["mail"]
                posts = GDB.get_posts(username)
                post_likes = []
                for post in posts:
                    post_likes.append(GDB.get_like_count(int(post["id"])))
                posts = zip(posts, post_likes)
                is_friend = GDB.is_friend(request.session['user']['username'], username)
                is_friend_request = GDB.has_send_friend_request(request.session['user']['username'], username)
                show_button = not (is_friend or is_friend_request)
                return render(request, 'search_profil.html', {"username":username,"name": name, "surname": surname, "age": age ,
                                                  "location": location, "sex": sex, "mail": mail, "posts": posts, "show_button": show_button, 'friends': friends})
            else:
                messages.error(request, f"User '{search_query}' not found.")
                return redirect('main_page')
    return render(request, 'main_page.html')

def filter_posts(request):
    if request.method == 'POST':
        keyword = request.POST.get('keyword', '')
        print("KEYWORD: ", keyword)
        if keyword:
            return redirect('main_page_filter', filter=keyword)
        else:
            return redirect('main_page')

def visit_profil(request, username):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    if username == request.session['user']['username']:
        return redirect('profil_page')
    is_friend = GDB.is_friend(request.session['user']['username'], username)
    is_friend_request = GDB.has_send_friend_request(request.session['user']['username'], username)
    if GDB.is_private(username) and not is_friend:
        show_button = not (is_friend or is_friend_request)
        return render(request, 'search_profil.html',
                      {'username': username, 'private': True, 'show_button': show_button, 'is_friend': is_friend})
    user_info = GDB.get_user_by_username(username)
    name = user_info["name"]
    surname = user_info["surname"]
    age = user_info["age"]
    location = user_info["location"]
    sex = user_info["sex"]
    mail = user_info["mail"]
    posts = GDB.get_posts(username)
    friends = GDB.get_friends(username)
    post_likes = []
    for post in posts:
        post_likes.append(int(GDB.get_like_count(post["id"])))
    posts = zip(posts, post_likes)
    is_friend = GDB.is_friend(request.session['user']['username'], username)
    is_friend_request = GDB.has_send_friend_request(request.session['user']['username'], username)
    show_button = not (is_friend or is_friend_request)
    return render(request, 'search_profil.html', {"username": username, "name": name, "surname": surname, "age": age,
                                                  "location": location, "sex": sex, "mail": mail, "posts": posts,
                                                  "show_button": show_button, "friends":friends})

def send_friend_request(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    sender = request.session['user']['username']
    receiver = request.POST['to_user']
    GDB.add_new_friend_request(sender, receiver)
    return redirect('main_page')

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

def private_messages_page(request, friend_username):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    username = request.session['user']['username']
    messages = GDB.get_messages(username, friend_username)
    return render(request, 'private_message.html', {'friend_username': friend_username, 'messages': messages})

def send_private_messages(request):
    username = request.session['user']['username']
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    if request.method == 'POST':
        friend_username = request.POST.get('friend_name')
        content_message = request.POST.get('send_message')
        if content_message:
            friend_username = request.POST.get('friend_name')
            GDB.create_message(username,friend_username, content_message)
            messages = GDB.get_messages(username, friend_username)
            return redirect('private_message_page', friend_username=friend_username)
    return redirect('private_message_page', friend_username=friend_username)


def add_comment(request, post_id):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    post = GDB.get_post_by_id(post_id)
    comments = GDB.get_comments(post_id)
    likes = GDB.get_like_count(post_id)
    print(comments)
    username = request.session['user']['username']
    print(post.element_id)
    post_id = int(post.element_id.split(':')[-1])
    print(post_id)
    if request.method == 'POST':
        content = request.POST.get('comment_content')
        if content:
            GDB.create_comment(post_id, content, username)
            post_author = GDB.get_post_by_id(post_id)["author"]
            content = f"{username} commented your post."
            GDB.create_notification(post_author, "comment", content)
            return redirect('add_comment', post_id=post_id)

    return render(request, 'add_comment.html', {'post': post, 'comments': comments, 'post_id': post_id, 'likes' : likes})

def group_list(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    username = request.session['user']['username']
    user_friends = GDB.get_friends(username)
    user_groups = GDB.get_groups(username)
    invitation_groups = GDB.get_groups_invitation(username)
    return render(request, 'group_list.html', {'user_friends' : user_friends, 'user_groups':user_groups, 'invitation_groups': invitation_groups, 'username':username})

def create_group(request):
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    username = request.session['user']['username']
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        invitation_list = request.POST.getlist('invite_users')
        GDB.create_group(group_name, username, invitation_list)
    return redirect('group_list')

def send_group_messages(request):
    username = request.session['user']['username']
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        content_message = request.POST.get('send_message')
        if content_message:
            print("GROUP NAME", group_name)
            GDB.create_group_message(username,group_name, content_message)
    return redirect('group_messages_page', group_name=group_name)

def group_messages_page(request, group_name):
    username = request.session['user']['username']
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    group_messages = GDB.get_group_messages(group_name)
    return render(request, 'group_message.html', {'group_messages':group_messages, 'group_name': group_name})

def accept_group_invitation_model(request, group_name):
    username = request.session['user']['username']
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    GDB.accept_invitation_group(username, group_name)
    return redirect('group_list')

def reject_group_invitation_model(request, group_name):
    username = request.session['user']['username']
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    GDB.refuse_invitation_group(username, group_name)
    print("GOUOP NALME",  group_name)
    return redirect('group_list')


def notifications_page(request):
    username = request.session['user']['username']
    GDB = graphDB("bolt://localhost:7687", "neo4j", "password")
    if not username:
        return redirect('login')

    notifications = GDB.get_notifications(username)
    unseen_notifications = GDB.get_unseen_notifications(username)
    unseen_notifications_id = []
    notifications_id = []
    print(unseen_notifications)
    for notif in unseen_notifications:
        unseen_notifications_id.append(int(notif.element_id.split(':')[-1]))
        GDB.mark_notification_as_seen(username, int(notif.element_id.split(':')[-1]))
    for notif in notifications:
        notifications_id.append(int(notif.element_id.split(':')[-1]))
    notifications = zip(notifications, notifications_id)
    return render(request, 'notifications.html', {'notifications' : notifications, 'unseen_notifications_id': unseen_notifications_id})