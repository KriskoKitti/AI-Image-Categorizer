from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from view.main_screen import MainScreen
from view.image_view_screen import ImageViewScreen
from view.upload_screen import UploadScreen
from view.search_screen import SearchScreen
from viewmodel.image_viewmodel import ImageViewModel

class RootScreenManager(ScreenManager):
    pass

class MyApp(App):
    def build(self):
        sm = RootScreenManager()

        viewmodel = ImageViewModel()
        
        sm.add_widget(MainScreen(viewmodel=viewmodel, name="main"))
        sm.add_widget(ImageViewScreen(viewmodel=viewmodel, name="viewer"))
        sm.add_widget(UploadScreen(viewmodel=viewmodel, name="upload"))
        sm.add_widget(SearchScreen(viewmodel=viewmodel, name="search"))
        return sm

MyApp().run()
