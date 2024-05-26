from PIL import Image

class Post:

    def __init__(self, content, media=None, media_type=None):
        self.content = content
        self.media = media
        self.media_type = media_type
        self.number_like = 0
        self.comments = [str]

    def like(self):
        self.number_like +=1

    def add_comment(self, content):
        self.comments.append(content)
