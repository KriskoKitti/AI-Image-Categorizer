from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.anchorlayout import AnchorLayout
import os
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
import threading
from kivy.clock import Clock
from kivy.factory import Factory

class UploadScreen(Screen):
    def __init__(self, viewmodel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel
        self.images_data = []   
        self.current_index = 0
    
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        contents = BoxLayout(orientation='horizontal', spacing=10, padding=10)
        left_panel = BoxLayout(orientation='vertical', size_hint_x=0.5)
    
        base_dir = os.path.dirname(os.path.dirname(__file__))
        assets_path = os.path.join(base_dir, "assets")

        self.file_chooser = FileChooserIconView(
            path=assets_path,
            filters=['*.png', '*.jpg', '*.jpeg']
        )
        self.file_chooser.size_hint_y = 0.9
        self.file_chooser.dirselect = False
        self.file_chooser.multiselect = True

        self.is_cancelled = False
        self.popup = None
        self.progress = None

        right_panel = BoxLayout(orientation='vertical', size_hint_x=0.5)
    
        self.preview = Image(size_hint_y=0.7, allow_stretch=True)
        self.tags_label = Label(
            text="Tags will appear here",
            size_hint_y=0.3,
            halign="left",
            valign="top",
            color=(119/255, 124/255, 109/255, 1)
        )
        self.tags_label.bind(size=self.update_label_size)

        nav_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        prev_btn = Factory.RoundedButton(text="<<")
        next_btn = Factory.RoundedButton(text=">>")

        prev_btn.bind(on_press=self.prev_image)
        next_btn.bind(on_press=self.next_image)

        nav_layout.add_widget(prev_btn)
        nav_layout.add_widget(next_btn)

        right_panel.add_widget(self.preview)
        right_panel.add_widget(self.tags_label)
        right_panel.add_widget(nav_layout)

        select_btn_layout = AnchorLayout(
            anchor_x='center',
            anchor_y='bottom',
            size_hint=(1, None),
            height=60
        )
        select_btn = Factory.RoundedButton(text="Upload", size_hint=(None, None), size=(400, 60))
        select_btn.bind(on_press=self.start_processing)
        select_btn_layout.add_widget(select_btn)

        left_panel.add_widget(self.file_chooser)
        left_panel.add_widget(select_btn_layout)

        contents.add_widget(left_panel)
        contents.add_widget(right_panel)
        layout.add_widget(contents)

        # Back button
        back_btn = Factory.RoundedButton(text="Back", size_hint_y=None, height=80, size_hint_x=None, width=100)
        back_btn.bind(on_press=self.go_back)
        back_layout = BoxLayout(size_hint_y=None, height=80, spacing=20)
        back_anchor = AnchorLayout(anchor_x='right', anchor_y='center')

        back_anchor.add_widget(back_btn)
        back_layout.add_widget(back_anchor)
        layout.add_widget(back_layout)

        self.add_widget(layout)  
        
    def go_back(self, instance):
        self.manager.current = "main"

    def show_current_image(self):
        if not self.images_data:
            return

        saved_path, result = self.images_data[self.current_index]

        if not os.path.exists(saved_path):
            print("Nem létezik a kép:", saved_path)
            return

        Clock.schedule_once(lambda dt: self.update_preview(saved_path, result), 0)

    def update_preview(self, filepath, result):
        self.preview.source = ""
        self.preview.reload()

        self.preview.source = filepath
        self.preview.reload()

        total = len(self.images_data)
        current = self.current_index + 1

        self.tags_label.text = (
            f"Caption: {result['caption']}\n"
            f"Category: {result['main_category']}/{result['subcategory']}\n"
            f"Tags: {', '.join(result['tags'])}\n"
            f"Date: {result.get('created_at')}\n"
            f"[{current}/{total}]\n"
        )

    def start_processing(self, instance):
        self.is_cancelled = False
        self.show_loading_popup()

        thread = threading.Thread(target=self.process_images)
        thread.start()

    def process_images(self):
        files = self.file_chooser.selection
        total = len(files)

        if total == 0:
            return

        for i, path in enumerate(files):
            if self.is_cancelled:
                break
            
            print(path)
            saved_path, result = self.viewmodel.organizer.add_image(path)
            self.images_data.append((saved_path, result))

            progress = (i + 1) / total * 100

            Clock.schedule_once(lambda dt, p=progress: self.update_progress(p))

        Clock.schedule_once(lambda dt: self.finish_processing())
        self.current_index = 0
        self.show_current_image()
                
    def show_loading_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.progress = ProgressBar(max=100, value=0)

        cancel_btn = Factory.RoundedButton(text="Megszakítás", size_hint_y=None, height=50)
        cancel_btn.bind(on_press=self.cancel_processing)

        layout.add_widget(self.progress)
        layout.add_widget(cancel_btn)

        self.popup = Popup(
            title="Feldolgozás...",
            content=layout,
            size_hint=(0.6, 0.3),
            auto_dismiss=False
        )

        self.popup.open()

    def update_progress(self, value):
        if self.progress:
            self.progress.value = value

    def cancel_processing(self, instance):
        self.is_cancelled = True

    def finish_processing(self):
        if self.popup:
            self.popup.dismiss()

    def next_image(self, instance):
        if self.current_index < len(self.images_data) - 1:
            self.current_index += 1
            self.show_current_image()


    def prev_image(self, instance):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_image()

    def update_label_size(self, instance, value):
        instance.text_size = (instance.width, None)