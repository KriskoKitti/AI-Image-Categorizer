from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
import os

class FolderWidget(ButtonBehavior, BoxLayout):
    def __init__(self, folder_name, callback, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=200, **kwargs)
        self.folder_name = folder_name
        self.callback = callback

        base_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(base_dir, "assets", "ui", "folder.png")
        
        self.img = Image(source=icon_path, size_hint=(1, 0.8))
        self.label = Label(text=folder_name, size_hint=(1, 0.2))

        self.add_widget(self.img)
        self.add_widget(self.label)

    def on_press(self):
        self.callback(self.folder_name)
