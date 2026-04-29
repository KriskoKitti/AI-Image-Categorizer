from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from view.main_screen import MainScreen
from view.image_view_screen import ImageViewScreen
from view.upload_screen import UploadScreen
from view.search_screen import SearchScreen
from viewmodel.image_viewmodel import ImageViewModel
from view.editor_screen import EditorScreen
from kivy.lang import Builder
import sys
import os
from kivy.core.window import Window

class RootScreenManager(ScreenManager):
    pass

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MyApp(App):
    def build(self):
        if sys.stdout is None:
            sys.stdout = open(os.devnull, "w")

        if sys.stderr is None:
            sys.stderr = open(os.devnull, "w")

        self.title = "AI Image Categorizer"
        sm = RootScreenManager()

        Window.clearcolor = (238/255, 238/255, 238/255, 1)
        Builder.load_file(resource_path("view/main_screen.kv"))

        viewmodel = ImageViewModel()
        
        sm.add_widget(MainScreen(viewmodel=viewmodel, name="main"))
        sm.add_widget(ImageViewScreen(viewmodel=viewmodel, name="viewer"))
        sm.add_widget(UploadScreen(viewmodel=viewmodel, name="upload"))
        sm.add_widget(SearchScreen(viewmodel=viewmodel, name="search"))
        sm.add_widget(EditorScreen(viewmodel=viewmodel, name="editor"))
        return sm

MyApp().run()
