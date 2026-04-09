from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from viewmodel.image_viewmodel import ImageViewModel
from .folder_widget import FolderWidget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.filechooser import FileChooserIconView
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
        self.back_btn = Button(text="Back")
        self.upload_btn = Button(text="Image upload")
        self.search_btn = Button(text="Image search")

        btn_layout.add_widget(self.back_btn)
        btn_layout.add_widget(self.upload_btn)
        btn_layout.add_widget(self.search_btn)

        root_layout.add_widget(btn_layout)

        # --- ScrollView (EGY!) ---
        self.scroll = ScrollView(size_hint=(1, 1))

        # --- Folder grid ---
        self.grid = GridLayout(cols=3, spacing=10, padding=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        # --- File list ---
        self.file_list = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        self.file_list.bind(minimum_height=self.file_list.setter('height'))

        # alapból mappák
        self.scroll.add_widget(self.grid)

        root_layout.add_widget(self.scroll)
        self.add_widget(root_layout)

        #--- Button event --- 
        self.viewmodel.bind(folders=self.update_folders) 
        self.upload_btn.bind(on_press=self.on_upload) 
        self.search_btn.bind(on_press=self.on_search) 
        self.back_btn.bind(on_press=self.on_back_pressed)

        self.update_folders(None, self.viewmodel.folders)
        

    def update_folders(self, instance, folders):
        self.grid.clear_widgets()

        for folder_data in folders:
            folder_widget = FolderWidget(
                folder_name=folder_data["name"],
                callback=self.on_folder_selected
            )
            self.grid.add_widget(folder_widget)

    def update_files(self, instance, images):
        self.file_list.clear_widgets()

        for image_path in images:
            file_item = self.create_file_item(image_path)
            self.file_list.add_widget(file_item)

    def on_enter(self):
        self.viewmodel.load_folders(self.viewmodel.current_path)
    
    def on_folder_selected(self, folder_name):
        self.viewmodel.select_folder(folder_name)

        if self.viewmodel.images and len(self.viewmodel.images) > 0:
            # Vannak képek → fájl nézet
            self.show_files()
        else:
            # Nincs kép → marad a mappa nézet
            self.show_folders()

    def on_upload(self, instance):
        self.manager.current = "upload"

    def on_search(self, instance):
        self.manager.current = "search"  

    def on_back_pressed(self, instance):
        self.viewmodel.go_back_folder()
        self.show_folders()
        
    def set_images(self, images_list):
        self.viewmodel.images = images_list
        
        if self.viewmodel.current_image not in images_list:
            self.viewmodel.index = 0
            if images_list:
                self.viewmodel.current_image = images_list[0]

    def show_folders(self):
        self.update_folders(None, self.viewmodel.folders)
        self.scroll.clear_widgets()
        self.scroll.add_widget(self.grid)
        self.grid.opacity = 1
        self.grid.disabled = False
        self.file_list.opacity = 0
        self.file_list.disabled = True

    def show_files(self):
        self.update_files(None, self.viewmodel.images)
        self.scroll.clear_widgets()
        self.scroll.add_widget(self.file_list)
        self.file_list.opacity = 1
        self.file_list.disabled = False
        self.grid.opacity = 0
        self.grid.disabled = True

    def create_file_item(self, img_path):
        layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=120,
            spacing=10,
            padding=10
        )

        with layout.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(150/255, 150/255, 150/255, 1)
            layout.rect = RoundedRectangle(radius=[10])

        # 📏 frissítés bind (EZ IS IDE)
        layout.bind(pos=self.update_rect, size=self.update_rect)

        # --- BAL OLDAL: KÉP ---
        img = Image(
            source=img_path,
            size_hint=(None, 1),
            width=120,
            allow_stretch=True,
            keep_ratio=True
        )

        # --- JOBB OLDAL: ADATOK ---
        info = BoxLayout(
            orientation='vertical',
            spacing=5
        )

        filename = os.path.basename(img_path)

        caption = self.viewmodel.get_caption(img_path)
        tags = ", ".join(self.viewmodel.get_tags(img_path))
        #date = self.viewmodel.get_upload_date(img_path)

        filename_label = Label(
        text=f"[b]{filename}[/b]",
        markup=True,
        halign='left',
        valign='middle'
        )
        filename_label.bind(size=filename_label.setter('text_size'))

        caption_label = Label(
            text=f"Caption: {caption}",
            halign='left',
            valign='middle'
        )
        caption_label.bind(size=caption_label.setter('text_size'))

        tags_label = Label(
            text=f"Tags: {tags}",
            halign='left',
            valign='middle'
        )
        tags_label.bind(size=tags_label.setter('text_size'))

        # date_label = Label(
        #     text=f"Dátum: {date}",
        #     halign='left',
        #     valign='middle'
        # )
        # date_label.bind(size=date_label.setter('text_size'))

        info.add_widget(filename_label)
        info.add_widget(caption_label)
        info.add_widget(tags_label)
        #info.add_widget(date_label)

        layout.add_widget(img)
        layout.add_widget(info)

        return layout
    
    def update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
