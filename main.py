from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.layout import Layout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, ObjectProperty
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from subprocess import Popen, PIPE
from kivy.uix.screenmanager import ScreenManager, Screen
import os, json


GAME_PATH = './game.exe'
BUTTON_COLOR = [0, 0, 0]
BUTTON_COLOR_ACTIVE = [1, 1, .4]
OPTIONS = ['Settings', 'Help']


class Background(Image):
    source = './bg.png'


Builder.load_string("""
<LauncherButton>:
    Button:
        id: button
        x: root.x
        y: root.y
        background_down: ''
        background_normal: ''
        background_color: root.background_color
        on_press: root.on_press()
        size_hint: 1, .9
        pos_hint: {'center_y' : .5}
    Label:
        text: root.text
        x: root.x
        y: root.y
""")

class LauncherButton(FloatLayout):
    text = StringProperty('')
    background_color = BUTTON_COLOR + [.4]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def on_touch_up(self, *a):
        self.ids['button'].background_color = BUTTON_COLOR + [.4]
        
    def on_press(self, *a):
        self.ids['button'].background_color = BUTTON_COLOR_ACTIVE + [.8]
        Clock.schedule_once(lambda dt: self.evaluate(), .1)
    
    def evaluate(self):
        pass


class HomeButton(LauncherButton):
    manager = ObjectProperty(None, allownone=True)

    def evaluate(self):
        manager = self.manager
        manager.transition.direction = 'right'
        manager.current = 'home'


class StartButton(LauncherButton):

    def evaluate(self):
        os.system(f'{GAME_PATH} launched')
        Window.minimize()# App.get_running_app().stop()


class SettingsButton(LauncherButton):

    def evaluate(self):
        manager = self.parent.parent.parent.parent.parent
        manager.transition.direction = 'left'
        manager.current = 'settings'


class HelpButton(LauncherButton):

    def evaluate(self):
        pass


class QuitButton(LauncherButton):

    def evaluate(self):
        App.get_running_app().stop()


class BaseLayout(Screen):
    pass


Builder.load_string("""
<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            Image:
                source: './title.png'
        BoxLayout:
            Widget:
            BoxLayout:
                id: buttons
                padding: 10 , 5
                orientation: 'vertical'
""")


class HomeScreen(BaseLayout):
    options = {
        'Settings': SettingsButton,
        'Help': HelpButton
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        buttons = self.ids['buttons']
        buttons.add_widget(StartButton(text='Start'))
        for o in OPTIONS:
            try:
                buttons.add_widget(self.options.get(o)(text=o))
            except:
                pass
        buttons.add_widget(QuitButton(text='Quit'))


Builder.load_string("""
<SettingsScreen>:
    BoxLayout:
        HomeButton:
            manager: root.parent
            text: '<'
            size_hint: None, None
            size: 50, 50
            pos_hint: {'top': 1}
        BoxLayout:
            padding: 5
            BoxLayout:
                canvas.before:
                    Color:
                        rgba: 0, 0, 0, .4
                    Rectangle:
                        size: self.size
                        pos: self.pos
""")


class SettingsScreen(BaseLayout):
    pass


class LauncherScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(HomeScreen(name='home'))
        self.add_widget(SettingsScreen(name='settings'))
        self.add_widget(Screen(name='help'))


Builder.load_string("""
<LauncherUI>:
    Image:
        id: bg_image
        source: './bg.png'
    LauncherScreenManager:
    Label:
        canvas.before:
            Color:
                rgba: 0, 0, 0, .5
            Rectangle:
                size:self.size
                pos: self.pos
        text: 'Version: 0.0.1'
        size_hint: None, None
        size: self.texture_size
        background_color: 0, 0, 0, .5
""")


class LauncherUI(FloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        width = self.ids['bg_image'].texture.size[0]
        height = self.ids['bg_image'].texture.size[1] - 37
        screen_width, screen_height = self.get_window_size()
        Window.top = screen_height/2 - height/2
        Window.left = screen_width/2 - width/2
        Window.borderless = True
        Window.fullscreen = False
        Window.size = (width, height)
        Clock.schedule_interval(self.fetch_data, 1)

    def get_window_size(self):
        sd = Popen('xrandr | grep "\*" | cut -d" " -f4',
                   shell=True,
                   stdout=PIPE).communicate()[0]
        splits = sd.decode("utf-8").split('x')

        try:
            a = splits[0]
            b = splits[1].split('\n')[0]
        except:
            a, b = (0, 0)
        return (int(a), int(b))

    def fetch_data(self, *a):
        try:
            open('./data.json')
        except:
            print('No data!')


class Launcher(App):
    def build(self):
        return LauncherUI()


if __name__ == '__main__':
    Launcher().run()