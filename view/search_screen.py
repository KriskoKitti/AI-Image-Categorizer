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

class ClickableBoxLayout(ButtonBehavior, BoxLayout):
    pass

class SearchScreen(Screen):
    def __init__(self, viewmodel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel
        self.images = []
        self.sort_mode = "name"
        self.active_tags = set()

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

        self.sort_btn = Factory.RoundedButton(text="Sort: Name", 
                               size_hint_x=None, 
                               width=300)
        self.sort_btn.bind(on_press=self.toggle_sort)

        self.filter_btn = Factory.RoundedButton(text="Filter tags", 
                                 size_hint_x=None, 
                                 width=300)
        self.filter_btn.bind(on_press=self.open_filter)

        sort_layout = BoxLayout(size_hint_y=None, height=80, spacing=20)
        sort_space = BoxLayout(size_hint_x=1)

        sort_layout.add_widget(sort_space)
        sort_layout.add_widget(self.sort_btn)
        sort_layout.add_widget(self.filter_btn)

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

        # self.viewmodel.bind(search_results=self.show_files)

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

        images = self.filter_images(images)
        images = self.sort_images(images)

        self.file_list.clear_widgets()

        for image_path in images:
            self.file_list.add_widget(self.create_file_item(image_path))

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
            height=140,
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

        layout.add_widget(img)
        layout.add_widget(info)
        layout.add_widget(edit_btn)

        layout.bind(on_press=lambda instance: self.open_viewer(img_path))

        return layout
    
     
    def update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def open_viewer(self, img_path):
        viewer = self.manager.get_screen("viewer")
        viewer.set_images([img_path])
        self.manager.current = "viewer"

    def filter_images(self, images):
        if not self.active_tags:
            return images

        result = []
        for img in images:
            tags = set(self.viewmodel.get_tags(img))
            if self.active_tags.intersection(tags):
                result.append(img)

        return result
    
    def sort_images(self, images):
        if self.sort_mode == "name":
            return sorted(images, key=lambda x: os.path.basename(x))

        elif self.sort_mode == "date":
            return sorted(images, key=lambda x: self.viewmodel.get_upload_date(x) or "")

        return images
    
    def filter_images(self, images):
        if not self.active_tags:
            return images

        return [
            img for img in images
            if self.active_tags.intersection(set(self.viewmodel.get_tags(img)))
        ]
    
    def toggle_sort(self, instance):
        if self.sort_mode == "name":
            self.sort_mode = "date"
            instance.text = "Sort: Date"
        else:
            self.sort_mode = "name"
            instance.text = "Sort: Name"

        self.refresh_files()

    def open_filter(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.tag_input = TextInput(hint_text="pl: animal, person")
        apply_btn = Button(text="Apply filter")

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

    def open_editor(self, img_path):
        editor_screen = self.manager.get_screen("editor")

        # átadjuk a kiválasztott képet
        editor_screen.load_image_data(img_path)

        self.manager.current = "editor"