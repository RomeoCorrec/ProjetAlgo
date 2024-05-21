from PIL import Image

class Post:

    def __init__(self, content, image=None):
        self.content = content
        self.images = image
        self.number_like = 0
        self.comments = [str]

    def like(self):
        self.number_like +=1

    def add_comment(self, content):
        self.comments.append(content)
