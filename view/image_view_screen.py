from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button

class ImageViewScreen(Screen):
    def __init__(self, viewmodel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel

        layout = BoxLayout(orientation='vertical')

        # --- Kép widget ---
        self.img_widget = Image()
        layout.add_widget(self.img_widget)

        # --- Prev/Next gombok ---
        btn_layout = BoxLayout(size_hint=(1, 0.1))
        prev_btn = Button(text="Prev")
        next_btn = Button(text="Next")
        btn_layout.add_widget(prev_btn)
        btn_layout.add_widget(next_btn)
        layout.add_widget(btn_layout)

        # --- Vissza gomb ---
        back_btn = Button(text="Vissza", size_hint=(1, 0.1))
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)

        self.add_widget(layout)

        # --- Bind ViewModelhez ---
        self.viewmodel.bind(current_image=self.update_image)

        # --- Gomb események ---
        prev_btn.bind(on_press=lambda x: self.viewmodel.prev_image())
        next_btn.bind(on_press=lambda x: self.viewmodel.next_image())

    def set_images(self, images_list):
        self.images = images_list
        self.idx = 0
        if self.images:
            self.img_widget.source = self.images[0]
            self.img_widget.reload()
    
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "main"

    def update_image(self, instance, value):
        """Frissíti a képet a VM current_image alapján"""
        if value:
            self.img_widget.source = value
            self.img_widget.reload()
