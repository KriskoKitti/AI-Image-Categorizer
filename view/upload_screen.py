from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
import os

class UploadScreen(Screen):
    def __init__(self, viewmodel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel
    
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
    
        self.file_chooser = FileChooserIconView(
            path="C:/Users/Win11/Documents/python/szakdoga/assets",
            filters=['*.png', '*.jpg', '*.jpeg']
        )
    
        self.preview = Image(size_hint=(1, 0.5))
        self.tags_label = Label(text="Tags itt jelennek meg")

        select_btn = Button(text="Kép feldolgozása")
        select_btn.bind(on_press=self.process_image)

        layout.add_widget(self.file_chooser)
        layout.add_widget(select_btn)
        layout.add_widget(self.preview)
        layout.add_widget(self.tags_label)

        # Back button
        back_btn = Button(text="Vissza", size_hint_y=None, height=50)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)

        self.add_widget(layout)  
        
    def go_back(self, instance):
        self.manager.current = "main"

    def process_image(self, instance):
        if self.file_chooser.selection:
            filepath = self.file_chooser.selection[0]

            self.preview.source = filepath
            self.preview.reload()

            saved_path, result = self.viewmodel.organizer.add_image(filepath)
    
            #Kiíratás
            tags = result["tags"]
            main_cat = result["main_category"]
            subcat = result["subcategory"]
            caption = result["caption"]
    
            self.tags_label.text = (
                f"Caption: {caption}\n"
                f"Kategória: {main_cat}/{subcat}\n"
                f"Tagek: {', '.join(tags)}\n"
                f"Mentve ide: {saved_path}"
            )
            
