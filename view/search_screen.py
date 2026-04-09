from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout

class SearchScreen(Screen):
    def __init__(self, viewmodel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel

        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        self.prompt_input = TextInput(hint_text="Your prompt...", size_hint_y=None, height=80)
        layout.add_widget(self.prompt_input)

        search_btn_layout = AnchorLayout(
            anchor_x='center',
            anchor_y='bottom',
            size_hint=(1, None),
            height=60
        )
        search_btn = Button(text="Search", size_hint=(None, None), size=(400, 60))
        search_btn.bind(on_press=self.on_search)
        search_btn_layout.add_widget(search_btn)
        layout.add_widget(search_btn_layout)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=3, spacing=10, padding=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)

        back_btn = Button(text="Back", size_hint_y=None, height=50)
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
            img_widget = Image(source=image_path, size_hint_y=None, height=250)
            self.grid.add_widget(img_widget)
