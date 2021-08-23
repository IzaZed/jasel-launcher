from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from subprocess import Popen, PIPE
import os


GAME_PATH = './game'

class Background(Image):
    source = './bg.png'


class LauncherButton(Button):
        
    def on_touch_up(self, *a):
        self.background_color = [0, 0, 0, .4]


Builder.load_string("""
<Menu>:
    Image:
        id: bg_image
        source: './bg.png'
    BoxLayout:
        orientation: 'vertical'
        Widget:
        BoxLayout:
            background_color: 0, 0, 0, .2
            Widget:
            BoxLayout:
                orientation: 'vertical'
                LauncherButton:
                    id: start_button
                    text: 'Start'
                    background_color: 0, 0, 0, .4
                    on_press: root.start(self)
                LauncherButton:
                    id: settings_button
                    text: 'Settings'
                    background_color: 0, 0, 0, .4
                    on_press: root.default(self)
                LauncherButton:
                    id: help_button
                    text: 'Help'
                    background_color: 0, 0, 0, .4
                    on_press: root.default(self)
                LauncherButton:
                    id: quit_button
                    text: 'Quit'
                    background_color: 0, 0, 0, .4
                    on_press: root.quit(self)
""")


class Menu(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__()
        width = self.ids['bg_image'].texture.size[0]
        height = self.ids['bg_image'].texture.size[1] - 37
        screen_width, screen_height = self.get_window_size()
        Window.top = screen_height/2 - height/2
        Window.left = screen_width/2 - width/2
        Window.borderless = True
        Window.fullscreen = False
        Window.size = (width, height)

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

    def start(self, w):
        w.background_color = [0, 0, 0, .8]
        Clock.schedule_once(lambda dt: self.launch(w), .05)
        
    def launch(self, w):
        try:
            os.system(f'{GAME_PATH} launched')
            App.get_running_app().stop()
        except:
            print('ERROR: Launcher file not found')
            App.get_running_app().stop()


    def quit(self, w):
        w.background_color = [0, 0, 0, .8]
        Clock.schedule_once(lambda dt: App.get_running_app().stop(), .05)

    def default(self, w):
        w.background_color = [0, 0, 0, .8]


class Launcher(App):
    def build(self):
        return Menu()


if __name__ == '__main__':
    Launcher().run()