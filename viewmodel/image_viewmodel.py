from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.event import EventDispatcher
from model.image_model import ImageModel
from model.image_organizer import ImageOrganizer
import os


class ImageViewModel(EventDispatcher):

    folders = ListProperty([])
    images = ListProperty([])
    current_image = StringProperty("")
    index = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = ImageModel()
        self.organizer = ImageOrganizer()
        self.base_path = self.get_assets_path()
        self.current_path = self.base_path
        self.load_folders(self.base_path)

    # ---------------- TAGS ----------------
    def process_image(self, image_path):
        return self.model.analyze_image(image_path)

    # ---------------- SAVE ----------------

    def save_image(self, image_path):
        return self.organizer.add_image(image_path)
    
    # ---------------- PATH ----------------

    def get_assets_path(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base_dir, "assets")

    # ---------------- FOLDERS ----------------

    def load_folders(self, path):
        self.current_path = path
        self.folders = self.model.get_subfolders(path)

    def select_folder(self, folder_name):
        next_path = os.path.join(self.current_path, folder_name)
    
        subfolders = self.model.get_subfolders(next_path)
        images = self.model.load_images(next_path)
    
        if subfolders:
            self.load_folders(next_path)
    
        elif images:
            self.images = images
            self.index = 0
            self.current_image = images[0]
    
        else:
            self.folders = []

    def go_back_folder(self):
        if self.current_path != self.base_path:
            self.current_path = os.path.dirname(self.current_path)
            self.load_folders(self.current_path)

    # ---------------- IMAGES ----------------

    def load_directory(self, directory):
        self.images = self.model.load_images(directory)
        self.index = 0

        if self.images:
            self.current_image = self.images[0]
        else:
            self.current_image = ""

    def next_image(self):
        if self.index < len(self.images) - 1:
            self.index += 1
            self.current_image = self.images[self.index]

    def prev_image(self):
        if self.index > 0:
            self.index -= 1
            self.current_image = self.images[self.index]
