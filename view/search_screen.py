from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

class SearchScreen(Screen):
    def __init__(self, viewmodel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel

        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        self.prompt_input = TextInput(hint_text="Írd be a keresett kulcsszót...", size_hint_y=None, height=40)
        layout.add_widget(self.prompt_input)

        search_btn = Button(text="Keresés", size_hint_y=None, height=50)
        search_btn.bind(on_press=self.on_search)
        layout.add_widget(search_btn)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=3, spacing=10, padding=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)

        back_btn = Button(text="Vissza", size_hint_y=None, height=50)
        back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "main"))
        layout.add_widget(back_btn)

        self.add_widget(layout)

        self.viewmodel.bind(search_results=self.update_results)

    def on_search(self, instance):
        prompt = self.prompt_input.text.strip()
        if prompt:
            self.viewmodel.search_images(prompt)

    def update_results(self, instance, results):
        self.grid.clear_widgets()
        for image_path in results:
            img_widget = Image(source=image_path, size_hint_y=None, height=150)
            self.grid.add_widget(img_widget)
