from Class import Post
from PIL import Image

class User:

    def __init__(self, username, name, surname, age, password, location, sex, mail):
        self.username = username
        self.name = name
        self.surname = surname
        self.age = age
        self.password = password
        self.location = location
        self.sex = sex
        self.mail = mail

        self.friends = [User]
        self.friends_requests_send = [User]
        self.friends_requests_received = [User]

        self.profile_description = ""
        self.profile_picture = Image
        self.interests = []

    def add_friends(self, user):
        self.friends_requests_send.append(user)
        # QUERY BDD waiting_for_answers

    def accept_friends(self, user):
        self.friends.append(user)
        self.friends_requests_received.remove(user)
        # QUERY BDD update relation

    def like_post(self, post: Post):
        post.like()
        #query bdd

    def comment_post(self, post: Post, content, image=None):
        post.comment(content, image)

    def send_private_message(self, content:str, user):
        #Query bdd
        return

    def send_group_message(self, group):
        #query bdd
        return

    #personalisation profile
    def update_description(self, content:str):
        self.profile_description = content

    def update_profile_picture(self, image):
        self.profile_picture = image

