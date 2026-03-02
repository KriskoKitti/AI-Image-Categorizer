from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from viewmodel.image_viewmodel import ImageViewModel
from .folder_widget import FolderWidget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import os

class MainScreen(Screen):
    def __init__(self, viewmodel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel
        self.assets_dir = self.viewmodel.get_assets_path()

        root_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # --- Buttons ---
        btn_layout = BoxLayout(size_hint_y=None, height=80, spacing=20)
        self.back_btn = Button(text="Vissza")
        self.upload_btn = Button(text="Kép feltöltés")
        self.search_btn = Button(text="Kép keresés")
        btn_layout.add_widget(self.back_btn)
        btn_layout.add_widget(self.upload_btn)
        btn_layout.add_widget(self.search_btn)
        root_layout.add_widget(btn_layout)

        # --- Folders ---
        scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=3, spacing=10, padding=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        root_layout.add_widget(scroll)

        self.add_widget(root_layout)

        # --- Button event ---
        self.viewmodel.bind(folders=self.update_folders)
        self.upload_btn.bind(on_press=self.on_upload)
        self.search_btn.bind(on_press=self.on_search)
        self.back_btn.bind(on_press=lambda x: self.viewmodel.go_back_folder())

        self.update_folders(None, self.viewmodel.folders)

    def update_folders(self, instance, folders):
        self.grid.clear_widgets()

        for folder_data in folders:
            folder_widget = FolderWidget(
                folder_name=folder_data["name"],
                callback=self.on_folder_selected
            )
            self.grid.add_widget(folder_widget)

    def on_enter(self):
        self.viewmodel.load_folders(self.viewmodel.current_path)
    
    def on_folder_selected(self, folder_name):
        self.viewmodel.select_folder(folder_name)
        if self.viewmodel.images:
            viewer_screen = self.manager.get_screen("viewer")
            viewer_screen.set_images(self.viewmodel.images)
            self.manager.current = "viewer"

    def on_upload(self, instance):
        self.manager.current = "upload"

    def on_search(self, instance):
        self.manager.current = "search"  
