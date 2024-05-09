from Post import Post


class User:

    def __init__(self, username, name, surname, age, password):
        self.username = username
        self.name = name
        self.surname = surname
        self.age = age
        self.password = password

        self.friends = [User]
        self.friends_requests_send = [User]
        self.friends_requests_received = [User]


    def add_friends(self, user: User):
        self.friends_requests_send.append(user)
        # QUERY BDD waiting_for_answers

    def accept_friends(self, user: User):
        self.friends.append(user)
        self.friends_requests_received.remove(user)
        # QUERY BDD update relation

    def like_post(self, post: Post):
        post.like()
        #query bdd

    def comment_post(self, post: Post, content, image=None):
        post.comment(content, image)

    def send_private_message(self, content:str, user:User):
        #Query bdd
        return

    def send_group_message(self, group):
        #query bdd
        return