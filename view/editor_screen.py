from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.uix.anchorlayout import AnchorLayout
import os

class EditorScreen(Screen):
    def __init__(self, viewmodel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel
        self.tags = []

        root = BoxLayout(orientation='horizontal', padding=10, spacing=10)
        right_box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        left_box = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # --- TOP BAR ---
        top_bar = BoxLayout(size_hint_y=None, height=50)

        back_btn = Factory.RoundedButton(text="Back", size_hint_x=None, width=100)
        back_btn.bind(on_press=self.go_back)

        save_btn = Factory.RoundedButton(text="Save")
        save_btn.bind(on_press=self.save_changes)

        top_bar.add_widget(save_btn)

        self.image = Image()
        right_box.add_widget(self.image)

        # --- Fájlnév ---
        self.filename_input = TextInput(
            hint_text="Fájlnév",
            size_hint_y=None,
            height=50
        )

        # --- Dátum ---
        self.date_input = TextInput(
            hint_text="Dátum (pl: 2024-01-01)",
            size_hint_y=None,
            height=50
        )

        # --- TAG LISTA ---
        self.tags_layout = BoxLayout(
            size_hint_y=None,
            height= 50,
            spacing=10
        )

        # --- Új tag input ---
        tag_input_layout = BoxLayout(size_hint_y=None, height=50)

        self.new_tag_input = TextInput(hint_text="Új tag")

        add_tag_btn = Factory.RoundedButton(text="+")
        add_tag_btn.bind(on_press=self.add_tag)

        tag_input_layout.add_widget(self.new_tag_input)
        tag_input_layout.add_widget(add_tag_btn)

        spacer = BoxLayout(size_hint_y=1)

        back_layout = BoxLayout(size_hint_y=None, height=80, spacing=20)
        back_anchor = AnchorLayout(anchor_x='right', anchor_y='center')

        back_anchor.add_widget(back_btn)
        back_layout.add_widget(back_anchor)

        # --- Tartalom összerakása ---
        left_box.add_widget(top_bar)
        left_box.add_widget(Label(text="Filename: ", 
                                  size_hint_y=None, 
                                  height=50,
                                  halign="left",
                                  valign="bottom",
                                  color=(119/255, 124/255, 109/255, 1)))
        left_box.add_widget(self.filename_input)
        left_box.add_widget(Label(text="Date:", 
                                  size_hint_y=None, 
                                  height=50,
                                  halign="left",
                                  valign="bottom",
                                  color=(119/255, 124/255, 109/255, 1)))
        left_box.add_widget(self.date_input)
        left_box.add_widget(Label(text="Tags:", 
                                  size_hint_y=None, 
                                  height=50,
                                  halign="left",
                                  valign="bottom",
                                  color=(119/255, 124/255, 109/255, 1)))
        left_box.add_widget(self.tags_layout)
        left_box.add_widget(tag_input_layout)
        left_box.add_widget(spacer)
        left_box.add_widget(back_layout)

        root.add_widget(right_box)
        root.add_widget(left_box)
        

        self.add_widget(root)



    def load_image_data(self, path):
        self.current_path = path
        self.image.source = path
        self.image.reload()

        filename = os.path.basename(path)
        date = self.viewmodel.get_upload_date(path)

        # --- Fájlnév input ---
        name, ext = os.path.splitext(filename)
        self.filename_input.text = name
        self.file_ext = ext

        # --- Dátum input ---
        self.date_input.text = str(date)

        # self.layout.add_widget(Label(text="Filename:"))
        # self.layout.add_widget(self.filename_input)

        # self.layout.add_widget(Label(text="Date:"))
        # self.layout.add_widget(self.date_input)

        self.tags = self.viewmodel.get_tags(path)
        self.refresh_tags()

    def go_back(self, instance):
        self.manager.current = "main"

    #------ Tagek -------
    def refresh_tags(self):
        self.tags_layout.clear_widgets()

        for tag in self.tags:
            btn = Factory.RoundedButton(text=tag, size_hint_x=None, width=100)
            btn.bind(on_press=self.remove_tag)
            self.tags_layout.add_widget(btn)

    def add_tag(self, instance):
        new_tag = self.new_tag_input.text.strip()

        if new_tag and new_tag not in self.tags:
            self.tags.append(new_tag)

        self.new_tag_input.text = ""
        self.refresh_tags()

    def remove_tag(self, instance):
        tag = instance.text
        if tag in self.tags:
            self.tags.remove(tag)

        self.refresh_tags()

    #------- Mentés ------

    def save_changes(self, instance):
        try:
            new_path = self.viewmodel.update_image_data(
                self.current_path,
                self.filename_input.text,
                self.date_input.text,
                self.tags
            )

            self.current_path = new_path
            self.manager.get_screen("main").show_files()
            self.manager.current = "main"

        except Exception as e:
            self.show_error(str(e))

    def show_error(self, message):
        layout = BoxLayout(orientation='vertical', spacing=10)

        label = Label(text=message)
        btn = Factory.RoundedButton(text="OK", size_hint=(1, 0.3))

        layout.add_widget(label)
        layout.add_widget(btn)

        popup = Popup(
            title="Hiba",
            content=layout,
            size_hint=(0.8, 0.4)
        )

        btn.bind(on_press=popup.dismiss)

        popup.open()
