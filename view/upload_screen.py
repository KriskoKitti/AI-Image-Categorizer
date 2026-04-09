from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.anchorlayout import AnchorLayout
import os

class UploadScreen(Screen):
    def __init__(self, viewmodel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel
    
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
        self.file_chooser.dirselect = True

        right_panel = BoxLayout(orientation='vertical', size_hint_x=0.5)
    
        self.preview = Image(size_hint_y=0.7)
        self.tags_label = Label(
            text="Tags will appear here",
            size_hint_y=0.3
        )

        select_btn_layout = AnchorLayout(
            anchor_x='center',
            anchor_y='bottom',
            size_hint=(1, None),
            height=60
        )
        select_btn = Button(text="Analyze image", size_hint=(None, None), size=(400, 60))
        select_btn.bind(on_press=self.process_image)
        select_btn_layout.add_widget(select_btn)

        # layout.add_widget(self.file_chooser)
        left_panel.add_widget(self.file_chooser)
        left_panel.add_widget(select_btn_layout)

        right_panel.add_widget(self.preview)
        right_panel.add_widget(self.tags_label)

        contents.add_widget(left_panel)
        contents.add_widget(right_panel)
        layout.add_widget(contents)

        # Back button
        back_btn = Button(text="Back", size_hint_y=None, height=80)
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
    
            tags = result["tags"]
            main_cat = result["main_category"]
            subcat = result["subcategory"]
            caption = result["caption"]
    
            self.tags_label.text = (
                f"Caption: {caption}\n"
                f"Category: {main_cat}/{subcat}\n"
                f"Tags: {', '.join(tags)}\n"
            )
            
