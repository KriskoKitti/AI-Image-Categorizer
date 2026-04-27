from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from view.main_screen import MainScreen
from view.image_view_screen import ImageViewScreen
from view.upload_screen import UploadScreen
from view.search_screen import SearchScreen
from viewmodel.image_viewmodel import ImageViewModel
from view.editor_screen import EditorScreen
from kivy.lang import Builder
from kivy.core.window import Window

class RootScreenManager(ScreenManager):
    pass

class MyApp(App):
    def build(self):
        self.title = "AI Image Categorizer"
        sm = RootScreenManager()

        Window.clearcolor = (238/255, 238/255, 238/255, 1)
        Builder.load_file("view/main_screen.kv")
        # Builder.load_file("view/upload.kv")
        # Builder.load_file("view/editor.kv")

        viewmodel = ImageViewModel()
        
        sm.add_widget(MainScreen(viewmodel=viewmodel, name="main"))
        sm.add_widget(ImageViewScreen(viewmodel=viewmodel, name="viewer"))
        sm.add_widget(UploadScreen(viewmodel=viewmodel, name="upload"))
        sm.add_widget(SearchScreen(viewmodel=viewmodel, name="search"))
        sm.add_widget(EditorScreen(viewmodel=viewmodel, name="editor"))
        return sm

MyApp().run()
