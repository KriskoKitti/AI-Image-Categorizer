from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import os
from kivy.properties import BooleanProperty

class ClickableBoxLayout(ButtonBehavior, BoxLayout):
    pass

class RoundedButton(Button):
    active = BooleanProperty(False)


class SearchScreen(Screen):
    def __init__(self, viewmodel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel
        self.images = []

        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        self.prompt_input = TextInput(hint_text="Your prompt...", size_hint_y=None, height=80)
        layout.add_widget(self.prompt_input)

        search_btn_layout = AnchorLayout(
            anchor_x='center',
            anchor_y='bottom',
            size_hint=(1, None),
            height=60
        )
        search_btn = Factory.RoundedButton(text="Search", size_hint=(None, None), size=(400, 60))
        search_btn.bind(on_press=self.on_search)
        search_btn_layout.add_widget(search_btn)
        layout.add_widget(search_btn_layout)
        
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)

        self.file_list = GridLayout(
            cols=1,
            spacing=10,
            padding=10,
            size_hint_y=None
        )

        self.file_list.bind(minimum_height=self.file_list.setter("height"))

        self.scroll.add_widget(self.file_list)
        layout.add_widget(self.scroll)

        back_btn = Factory.RoundedButton(text="Back", size_hint_y=None, height=80, size_hint_x=None, width=100)
        back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "main"))

        back_layout = BoxLayout(size_hint_y=None, height=80, spacing=20)
        back_anchor = AnchorLayout(anchor_x='right', anchor_y='center')

        back_anchor.add_widget(back_btn)
        back_layout.add_widget(back_anchor)
        layout.add_widget(back_layout)

        self.add_widget(layout)



    def on_search(self, instance):
        prompt = self.prompt_input.text.strip()

        if prompt:
            self.images = self.viewmodel.search_images(prompt)
            self.refresh_files()

    def update_results(self, instance, results):
        self.grid.clear_widgets()
        for image_path in results:
            img_widget = Image(source=image_path, size_hint_y=None, height=250)
            self.grid.add_widget(img_widget)

    def refresh_files(self):
        images = self.images

        self.file_list.clear_widgets()

        for image_path in images:
            self.file_list.add_widget(self.create_file_item(image_path))

        Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", 1))

    def show_files(self, instance, results):
        self.refresh_files()
        self.scroll.clear_widgets()
        self.scroll.add_widget(self.file_list)
        self.file_list.opacity = 1
        self.file_list.disabled = False
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 1))

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
            text=f"Dátum: {date}",
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

        edit_btn.bind(on_press=lambda x: self.open_editor(img_path))

        delete_btn = Factory.RoundedButton(
            text="Delete",
            size_hint=(None, 1),
            width=120
        )

        delete_btn.bind(on_press=lambda x, path=img_path: self.confirm_delete(path))

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
        editor_screen.return_screen = "search"
        self.manager.current = "editor"

    def confirm_delete(self, img_path):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)

        content.add_widget(Label(text="Are you sure you want to delete this image?"))

        buttons = BoxLayout(size_hint_y=None, height=50, spacing=10)

        cancel_btn = Button(text="Cancel")
        delete_btn = Button(text="Delete")

        buttons.add_widget(cancel_btn)
        buttons.add_widget(delete_btn)

        content.add_widget(buttons)

        popup = Popup(
            title="Delete image",
            content=content,
            size_hint=(0.6, 0.35),
            auto_dismiss=False
        )

        cancel_btn.bind(on_press=popup.dismiss)

        def delete_confirmed(instance):
            self.viewmodel.delete_image(img_path)

            if img_path in self.images:
                self.images.remove(img_path)

            popup.dismiss()
            self.refresh_files()

        delete_btn.bind(on_press=delete_confirmed)

        popup.open()