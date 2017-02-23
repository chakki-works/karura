import os
import tempfile
from contextlib import contextmanager
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class ImageFile():

    def __init__(self, fd, path, title):
        self.fd = fd
        self.path = path
        self.title = title
    
    @classmethod
    def create(cls, title=""):
        fd, temp_path = tempfile.mkstemp(suffix=".png", prefix="karura")
        return ImageFile(fd, temp_path, title)
    
    @contextmanager
    def plot(self):
        plt.style.use("ggplot")
        plt.rcParams["font.family"] = "Yu Mincho"
        fig = plt.figure()

        yield fig

        plt.tight_layout()
        fig.savefig(self.path)

    def delete(self):
        os.close(self.fd)
        os.remove(self.path)
        self.fd = ""
        self.path = ""


class Description():

    def __init__(self, desc, picture=None):
        self.desc = desc
        self.picture = picture

    def __str__(self):
        return self.desc
    
    def send_reply(self, slack_message):
        if self.picture:
            title = self.picture.title if self.picture.title else "picture"
            slack_message.channel.upload_file(title, self.picture.path, self.desc)
            self.picture.delete()
        else:
            slack_message.reply(self.desc)
    
    def delete(self):
        if self.picture is not None and self.picture.path:
            self.picture.delete()
