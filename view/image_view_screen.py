from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.factory import Factory
from kivy.uix.anchorlayout import AnchorLayout

class ImageViewScreen(Screen):
    def __init__(self, viewmodel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel

        layout = BoxLayout(orientation='vertical')

        # --- Kép widget ---
        self.img_widget = Image()
        layout.add_widget(self.img_widget)

        # --- Vissza gomb ---
        back_btn = Factory.RoundedButton(text="Back", size_hint_y=1, size_hint_x=None, width=100)
        back_btn.bind(on_press=self.go_back)

        back_layout = BoxLayout(size_hint_y=None, height=80, spacing=20)
        back_anchor = AnchorLayout(anchor_x='right', anchor_y='center')

        back_anchor.add_widget(back_btn)
        back_layout.add_widget(back_anchor)
        layout.add_widget(back_layout)

        self.add_widget(layout)

    def on_enter(self):
        self.viewmodel.bind(current_image=self.update_image)
        if self.viewmodel.current_image:
            self.update_image(None, self.viewmodel.current_image)

    def on_leave(self): 
        self.viewmodel.unbind(current_image=self.update_image)

    def set_images(self, images_list):
        self.viewmodel.images = images_list
        self.viewmodel.index = 0
        
        if images_list:
            self.viewmodel.current_image = images_list[0]
    
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "main"

    def update_image(self, instance, value):
        if value:
            self.img_widget.source = value
            self.img_widget.reload()
