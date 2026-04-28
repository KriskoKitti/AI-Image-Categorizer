from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from .folder_widget import FolderWidget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.filechooser import FileChooserIconView
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import os
from kivy.uix.anchorlayout import AnchorLayout
from kivy.factory import Factory
from kivy.properties import BooleanProperty

class ClickableBoxLayout(ButtonBehavior, BoxLayout):
    pass

class RoundedButton(Button):
    active = BooleanProperty(False)

class MainScreen(Screen):
    def __init__(self, viewmodel, **kwargs):
        super().__init__(**kwargs)
        self.ITEM_WIDTH = 200
        self.ITEM_HEIGHT = 180


        self.viewmodel = viewmodel
        self.assets_dir = self.viewmodel.get_assets_path()
        self.sort_mode = "name_asc"   
        self.active_tags = set()  

        root_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # --- Buttons ---
        menu_layout = BoxLayout(size_hint_y=None, height=80, spacing=20)
        self.back_btn = Factory.RoundedButton(text="Back", 
                               size_hint_x=None, 
                               width=100)
        self.upload_btn = Factory.RoundedButton(text="Image upload", 
                                 size_hint_x=None, 
                                 width=300)
        self.search_btn = Factory.RoundedButton(text="Image search", 
                                 size_hint_x=None, width=300)

        self.sort_name_btn = Factory.RoundedButton(
            text="Name (A-Z)",
            size_hint_x=None,
            width=200
        )

        self.sort_date_btn = Factory.RoundedButton(
            text="Date",
            size_hint_x=None,
            width=200
        )
        self.sort_name_btn.bind(on_press=self.toggle_name_sort)
        self.sort_date_btn.bind(on_press=self.toggle_date_sort)
        self.sort_name_btn.active = True
        self.sort_date_btn.active = False

        self.filter_btn = Factory.RoundedButton(text="Filter tags", 
                                 size_hint_x=None, 
                                 width=300)
        self.filter_btn.bind(on_press=self.open_filter)

        menu_layout.add_widget(self.upload_btn)
        menu_layout.add_widget(self.search_btn)

        sort_layout = BoxLayout(size_hint_y=None, height=80, spacing=20)
        sort_space = BoxLayout(size_hint_x=1)

        sort_layout.add_widget(sort_space)
        sort_layout.add_widget(self.sort_name_btn)
        sort_layout.add_widget(self.sort_date_btn)
        sort_layout.add_widget(self.filter_btn)

        self.path_label = Label(
            text="",
            size_hint_y=None,
            height=40,
            halign="left",
            valign="middle",
            color=(119/255, 124/255, 109/255, 1)
        )
        self.path_label.bind(size=self.path_label.setter("text_size"))

        # --- ScrollView ---
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)

        # --- Folder grid ---
        self.grid = GridLayout(cols=3, spacing=10, padding=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        # --- File list ---
        self.file_list = ClickableBoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        self.file_list.bind(minimum_height=lambda instance, value: setattr(self.file_list, 'height', value))

        # alapból mappák
        self.scroll.add_widget(self.grid)

        back_layout = BoxLayout(size_hint_y=None, height=80, spacing=20)
        back_anchor = AnchorLayout(anchor_x='right', anchor_y='center')

        back_anchor.add_widget(self.back_btn)
        back_layout.add_widget(back_anchor)

        root_layout.add_widget(menu_layout)
        root_layout.add_widget(sort_layout)
        root_layout.add_widget(self.path_label)
        root_layout.add_widget(self.scroll)
        root_layout.add_widget(back_layout)
        self.add_widget(root_layout)

        #--- Button event --- 
        self.viewmodel.bind(folders=self.update_folders) 
        self.upload_btn.bind(on_press=self.on_upload) 
        self.search_btn.bind(on_press=self.on_search) 
        self.back_btn.bind(on_press=self.on_back_pressed)

        self.bind(size=self.update_columns)
        Clock.schedule_once(lambda dt: self.update_columns())
        self.update_folders(None, self.viewmodel.folders)

        self.set_file_controls_enabled(False)
        self.update_filter_button()
        
    def update_columns(self, *args):
        if self.width == 0:
            return

        spacing = self.grid.spacing[0] if isinstance(self.grid.spacing, (list, tuple)) else self.grid.spacing

        cols = max(1, int(self.width / (self.ITEM_WIDTH + spacing)))
        self.grid.cols = cols

    def update_folders(self, instance, folders):
        self.grid.clear_widgets()

        if self.viewmodel.current_path != self.viewmodel.base_path:
            back_widget = FolderWidget(
                folder_name="\..",
                callback=lambda x: self.on_back_pressed(None),
                size_hint = (None, None),
                size=(self.ITEM_WIDTH, self.ITEM_HEIGHT)
            )
            back_widget.label.color = (119/255, 124/255, 109/255, 1)
            self.grid.add_widget(back_widget)

        for folder_data in folders:
            folder_widget = FolderWidget(
                folder_name=folder_data["name"],
                callback=self.on_folder_selected
            )
            folder_widget.size_hint = (None, None)
            folder_widget.size = (self.ITEM_WIDTH, self.ITEM_HEIGHT)
            folder_widget.label.color=(119/255, 124/255, 109/255, 1)
            self.grid.add_widget(folder_widget)

    def update_path_label(self):
        rel_path = os.path.relpath(
            self.viewmodel.current_path,
            self.viewmodel.base_path
        )

        if rel_path == ".":
            self.path_label.text = "\\images"
        else:
            self.path_label.text = "\\images > " + rel_path.replace(os.sep, " > ")

    def refresh_files(self):
        images = self.viewmodel.images

        images = self.filter_images(images)
        images = self.sort_images(images)

        self.file_list.clear_widgets()

        for image_path in images:
            self.file_list.add_widget(self.create_file_item(image_path))

    def on_enter(self):
        self.viewmodel.load_folders(self.viewmodel.current_path)
        self.update_path_label()

    def on_pre_enter(self):
        self.viewmodel.load_folders(self.viewmodel.current_path)
    
    def on_folder_selected(self, folder_name):
        self.viewmodel.select_folder(folder_name)

        if self.viewmodel.images and len(self.viewmodel.images) > 0:
            self.show_files()
        else:
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
        self.update_path_label()
        self.update_folders(None, self.viewmodel.folders)
        self.scroll.clear_widgets()
        self.scroll.add_widget(self.grid)
        self.grid.opacity = 1
        self.grid.disabled = False
        self.file_list.opacity = 0
        self.file_list.disabled = True
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 1))

        self.set_file_controls_enabled(False)

    def show_files(self):
        self.update_path_label()
        self.refresh_files()
        self.scroll.clear_widgets()
        self.scroll.add_widget(self.file_list)
        self.file_list.opacity = 1
        self.file_list.disabled = False
        self.grid.opacity = 0
        self.grid.disabled = True
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 1))

        self.set_file_controls_enabled(True)

    def create_file_item(self, img_path):
        layout = ClickableBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=150,
            spacing=10,
            padding=10
        )

        with layout.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(183/255, 184/255, 159/255, 1)
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
        date = self.viewmodel.get_upload_date(img_path)

        filename_label = Label(
            text=f"[b]{filename}[/b]",
            markup=True,
            halign='left',
            valign='middle',
            color=(119/255, 124/255, 109/255, 1)
        )
        filename_label.bind(size=filename_label.setter('text_size'))

        caption_label = Label(
            text=f"Caption: {caption}",
            halign='left',
            valign='middle',
            color=(119/255, 124/255, 109/255, 1)
        )
        caption_label.bind(size=caption_label.setter('text_size'))

        tags_label = Label(
            text=f"Tags: {tags}",
            halign='left',
            valign='middle',
            color=(119/255, 124/255, 109/255, 1)
        )
        tags_label.bind(size=tags_label.setter('text_size'))

        date_label = Label(
            text=f"Date: {date}",
            halign='left',
            valign='middle',
            color=(119/255, 124/255, 109/255, 1)
        )
        date_label.bind(size=date_label.setter('text_size'))

        info.add_widget(filename_label)
        info.add_widget(caption_label)
        info.add_widget(tags_label)
        info.add_widget(date_label)

        edit_btn = Factory.RoundedButton(
            text="Edit",
            size_hint=(None, 1),
            width=100
        )

        delete_btn = Factory.RoundedButton(
            text="Delete",
            size_hint=(None, 1),
            width=120
        )

        delete_btn.bind(on_press=lambda x, path=img_path: self.confirm_delete(path))

        edit_btn.bind(on_press=lambda x: self.open_editor(img_path))

        layout.add_widget(img)
        layout.add_widget(info)
        layout.add_widget(edit_btn)
        layout.add_widget(delete_btn)

        layout.bind(on_press=lambda instance: self.open_viewer(img_path))

        return layout
    
    def update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def open_viewer(self, img_path):
        viewer = self.manager.get_screen("viewer")
        viewer.set_images([img_path])
        self.manager.current = "viewer"

    def open_editor(self, img_path):
        editor_screen = self.manager.get_screen("editor")
        editor_screen.load_image_data(img_path)
        editor_screen.return_screen = "main"
        self.manager.current = "editor"

    # ------- SORTING / FILTER ---------
    def sort_images(self, images):
        if self.sort_mode == "name_asc":
            return sorted(images, key=lambda x: os.path.basename(x).lower())

        if self.sort_mode == "name_desc":
            return sorted(images, key=lambda x: os.path.basename(x).lower(), reverse=True)

        if self.sort_mode == "date_asc":
            return sorted(images, key=lambda x: self.viewmodel.get_upload_date(x) or "")

        if self.sort_mode == "date_desc":
            return sorted(images, key=lambda x: self.viewmodel.get_upload_date(x) or "", reverse=True)

        return images
    
    def filter_images(self, images):
        if not self.active_tags:
            return images

        result = []
        for img in images:
            tags = set(self.viewmodel.get_tags(img))
            if self.active_tags.intersection(tags):
                result.append(img)

        return result

    def refresh_files(self):
        images = self.viewmodel.images

        images = self.filter_images(images)
        images = self.sort_images(images)

        self.file_list.clear_widgets()

        for image_path in images:
            self.file_list.add_widget(self.create_file_item(image_path))

    def toggle_name_sort(self, instance):
        if self.sort_mode == "name_asc":
            self.sort_mode = "name_desc"
        else:
            self.sort_mode = "name_asc"

        self.update_sort_buttons()
        self.refresh_files()

    def toggle_date_sort(self, instance):
        if self.sort_mode == "date_asc":
            self.sort_mode = "date_desc"
        else:
            self.sort_mode = "date_asc"

        self.update_sort_buttons()
        self.refresh_files()

    def update_sort_buttons(self):

        # Name gomb
        if "name" in self.sort_mode:
            self.sort_name_btn.active = True
            self.sort_name_btn.text = "Name (A-Z)" if self.sort_mode == "name_asc" else "Name (Z-A)"
        else:
            self.sort_name_btn.active = False
            self.sort_name_btn.text = "Name"

        # Date gomb
        if "date" in self.sort_mode:
            self.sort_date_btn.active = True
            self.sort_date_btn.text = "Date increase" if self.sort_mode == "date_asc" else "Date decrease"
        else:
            self.sort_date_btn.active = False
            self.sort_date_btn.text = "Date"

    def set_tag_filter(self, tags):
        self.active_tags = set(tag.strip().lower() for tag in tags if tag.strip())
        self.update_filter_button()
        self.refresh_files()

    def update_filter_button(self):
        if self.active_tags:
            tags_text = ", ".join(sorted(self.active_tags))
            self.filter_btn.text = f"Filter: {tags_text}  X"
            self.filter_btn.active = True
        else:
            self.filter_btn.text = "Filter tags"
            self.filter_btn.active = False

    def open_filter(self, instance):
        if self.active_tags:
            self.active_tags.clear()
            self.update_filter_button()
            self.refresh_files()
            return

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.tag_input = TextInput(hint_text="pl: animal, person")
        apply_btn = RoundedButton(text="Apply filter")

        layout.add_widget(self.tag_input)
        layout.add_widget(apply_btn)

        popup = Popup(
            title="Filter by tags",
            content=layout,
            size_hint=(0.6, 0.4)
        )

        def apply(_):
            tags = [t.strip() for t in self.tag_input.text.split(",") if t.strip()]
            self.set_tag_filter(tags)
            popup.dismiss()

        apply_btn.bind(on_press=apply)
        popup.open()

    def set_file_controls_enabled(self, enabled):
        self.sort_name_btn.disabled = not enabled
        self.sort_date_btn.disabled = not enabled
        self.filter_btn.disabled = not enabled

        self.sort_name_btn.opacity = 1 if enabled else 0.6
        self.sort_date_btn.opacity = 1 if enabled else 0.6
        self.filter_btn.opacity = 1 if enabled else 0.6

    def confirm_delete(self, img_path):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)

        content.add_widget(Label(text="Are you sure you want to delete this image?"))

        btns = BoxLayout(size_hint_y=None, height=50, spacing=10)

        cancel_btn = Button(text="Cancel")
        delete_btn = Button(text="Delete")

        btns.add_widget(cancel_btn)
        btns.add_widget(delete_btn)
        content.add_widget(btns)

        popup = Popup(
            title="Delete image",
            content=content,
            size_hint=(0.6, 0.35),
            auto_dismiss=False
        )

        cancel_btn.bind(on_press=popup.dismiss)

        def delete_confirmed(instance):
            self.viewmodel.delete_image(img_path)
            popup.dismiss()
            self.refresh_files()

        delete_btn.bind(on_press=delete_confirmed)

        popup.open()