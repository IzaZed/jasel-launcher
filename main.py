from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from subprocess import Popen, PIPE
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.effects.scroll import ScrollEffect
import os, json, pathlib, platform

# USER DATA ####################################################################
#
# Path to the executable, must be relative to the launcher
GAME_PATH = 'game.exe'
#
# Path to the settings file (if there is one), must be relative to the launcher
SETTINGS_FILE = 'settings.json'
#
# Path to the background image, must be relative to the launcher
BG_IMAGE = 'bg.png'
#
# Wether the Buttons are on the left or on the right side
BUTTON_ORIENTATION = 'right'
#
# Button Color
BUTTON_COLOR = [0, 0, 0, .4]
#
# Button Color when pressed
BUTTON_COLOR_ACTIVE = [1, 1, .4, .8]
#
# Font Color
FONT_COLOR = [1, 1, .8]
#
# Options to be shown in the main menu; Available are Settings, Help, Mods
OPTIONS = ['Settings', 'Help', 'Mods']
#
# Roundness of the Buttons and fields
UI_RADIUS = 3
################################################################################

current_path = pathlib.Path(__file__).parent.resolve()


class LauncherElement():
    roundness = [UI_RADIUS,]
    font_color = FONT_COLOR


Builder.load_string("""
<EmptyButton>:
    background_down: ''
    background_normal: ''
    background_color: 0, 0, 0, 0
""")


class EmptyButton(Button):
    pass


Builder.load_string("""
<SettingsItem>:
""")

class SettingsItem(BoxLayout):
    content = ObjectProperty(False)
    pass

Builder.load_string("""
<SettingsCheckbox>:
    background_down: ''
    background_normal: ''
    background_color: 0, 0, 0, 0
    canvas.before:
        Color:
            rgba: root.color_active if root.content else root.color_inactive
        RoundedRectangle:
            radius: root.roundness
            pos: self.pos[0] + self.width/2 - self.size[1]*.6 / 2, self.pos[1] + (self.size[1]*.4/2)
            size: self.size[1]*.6, self.size[1]*.6
""")


class SettingsCheckbox(SettingsItem, LauncherElement, Button):
    color_active = ListProperty(BUTTON_COLOR_ACTIVE)
    color_inactive = ListProperty(BUTTON_COLOR)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_active[3] = 1
        self.color_inactive[3] = 1

    def on_press(self, *a):
        self.content = not self.content


Builder.load_string("""
<SelectedItemUI>:
    canvas.before:
        Color:
            rgba: root.color
        Rectangle:
            size: self.width - 5, self.height
            pos: self.x + 2.5, self.y + 2.5
""")


class SelectedItemUI(Widget):
    color = ListProperty(BUTTON_COLOR)
    idx = NumericProperty(0)


Builder.load_string("""
<SettingsList>:
    orientation: 'vertical'
    BoxLayout:
        size_hint_x: None
        width: root.width * .9
        pos_hint: {'center_x': .5}
        LauncherButton:
            text: '<'
            size_hint: None, None
            height: root.height * .7
            width: self.height
            pos_hint: {'center_y': .5}
            on_evaluate: root.prev_item()
        Label:
            text: root.content
            font_size: self.height * .5
            color: root.font_color
        LauncherButton:
            text: '>'
            size_hint: None, None
            height: root.height * .7
            width: self.height
            pos_hint: {'center_y': .5}
            on_evaluate: root.next_item()
    BoxLayout:
        id: selection_ui
        size_hint_x: None
        width: root.width * .7
        pos_hint: {'center_x': .5}
        size_hint_y: .1 
""")


class SettingsList(SettingsItem, LauncherElement):
    color_active = ListProperty(BUTTON_COLOR_ACTIVE)
    color_inactive = ListProperty(BUTTON_COLOR)
    options = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.index = self.options.index(self.content)
        for i, o in enumerate(self.options):
            self.ids['selection_ui'].add_widget(SelectedItemUI(idx=i))
        self.color_active[3] = 1
        self.color_inactive[3] = 1
        self.set_selection_ui()

    def next_item(self, *a):
        self.index += 1
        if self.index > len(self.options) - 1:
            self.index = 0
        self.content = self.options[self.index]
        self.set_selection_ui()

    def prev_item(self, *a):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.options) - 1
        self.content = self.options[self.index]
        self.set_selection_ui()
    
    def set_selection_ui(self):
        for item in self.ids['selection_ui'].children:
            item.color = BUTTON_COLOR_ACTIVE if item.idx == self.index else BUTTON_COLOR


Builder.load_string("""
<SettingsLabel>:
    text: str(root.content)
""")
class SettingsLabel(SettingsItem):
    pass


Builder.load_string("""
<LauncherButton>:
    Button:
        canvas.before:
            Color:
                rgba: root.background_color
            RoundedRectangle:
                radius: root.roundness
                size: self.size
                pos: self.pos   
        id: button
        size_hint: None, None
        size: root.width - 5, root.height - 5
        background_down: ''
        background_normal: ''
        background_color: [0, 0, 0, 0]
        on_press: root.on_press()
        pos_hint: {'center_y' : .5, 'center_x': .5}
    Label:
        text: root.text
        x: root.width * .05
        font_size: self.height * .6 if root.height < root.width else root.width
        color: root.font_color
        size_hint_x: None
        width: self.texture_size[0] if root.height < root.width else root.width
        align: 'left'
""")

class LauncherButton(RelativeLayout, LauncherElement):
    text = StringProperty('')
    font_color = ListProperty(FONT_COLOR)
    background_color = ListProperty(BUTTON_COLOR)
    def __init__(self, **kwargs):#
        self.register_event_type('on_evaluate')
        super().__init__(**kwargs)

    def on_press(self, *a):
        self.background_color = BUTTON_COLOR_ACTIVE
        Clock.schedule_once(lambda dt: self.reset(), .05)
    
    def reset(self):
        self.background_color = BUTTON_COLOR
        self.dispatch('on_evaluate')

    def on_evaluate(self, *a):
        pass

Builder.load_string("""
<LauncherOptionButton>:
    Label:
        text: '>'
        x: root.width - self.width - 20
        font_size: self.height / 2
        color: root.font_color
        size_hint_x: None
        width: self.texture_size[0]
        align: 'right'
""")


class LauncherOptionButton(LauncherButton):
    pass


class HomeButton(LauncherButton):
    manager = ObjectProperty(None, allownone=True)

    def on_evaluate(self, *a):
        manager = self.manager
        manager.transition.direction = 'right'
        manager.current = 'home'
        with open(f'{os.path.join(current_path, SETTINGS_FILE)}') as f:
            data = json.load(f)
            for s in reversed(self.parent.parent.parent.ids['settings_area'].children):
                key, value = s.retrieve_data()
                data.get(key)[0] = value
        with open((f'{os.path.join(current_path, SETTINGS_FILE)}'), 'w') as f:
            json.dump(data, f, indent=2)
            f.close()


class StartButton(LauncherOptionButton):

    def on_evaluate(self, *a):
        os.system(f'{os.path.join(current_path, GAME_PATH)} launched')
        Window.minimize()# App.get_running_app().stop()


class SettingsButton(LauncherOptionButton):

    def on_evaluate(self, *a):
        manager = self.parent.parent.parent.parent.parent
        manager.transition.direction = 'left'
        manager.current = 'settings'


class ModsButton(LauncherOptionButton):

    def on_evaluate(self, *a):
        pass


class HelpButton(LauncherOptionButton):

    def on_evaluate(self, *a):
        pass


class QuitButton(LauncherOptionButton):

    def on_evaluate(self, *a):  
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
            BoxLayout:
                id: left
                padding: 5 , 5
                orientation: 'vertical'
            BoxLayout:
                id: right
                padding: 5 , 5
                orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: 15
""")


class HomeScreen(BaseLayout):
    options = {
        'Settings': SettingsButton,
        'Help': HelpButton,
        'Mods': ModsButton
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        buttons = self.ids[BUTTON_ORIENTATION]
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
        orientation: 'vertical'
        BoxLayout:
            padding: 5
            HomeButton:
                manager: root.parent
                text: '<'
                y: root.height - self.height
                x: 0
                size_hint_x: None
                width: 50
            BoxLayout:
                padding: 5
                canvas.before:
                    Color:
                        rgba: root.background_color
                    RoundedRectangle:
                        radius: root.roundness
                        size: self.width - 5, self.height - 5
                        pos: self.x + 2.5, self.y + 2.5
                ScrollView:
                    id: scroll
                    bar_width: 50
                    always_overscroll: False
                    BoxLayout:
                        id: settings_area
                        size_hint_y: None
                        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: 15
""")


class SettingsScreen(BaseLayout, LauncherElement):
    background_color = BUTTON_COLOR
    def __init__(self, **kw):
        super().__init__(**kw)
        self.ids['scroll'].effect_cls = ScrollEffect
        with open((f'{os.path.join(current_path, SETTINGS_FILE)}')) as f:
            data = json.load(f)
            for x in data:
                self.ids['settings_area'].add_widget(SettingsLine(setting=x, content=data[x]))
            self.ids['settings_area'].height = len(data) * 40
            f.close()


Builder.load_string("""
<SettingsLine>:
    orientation: 'vertical'
    size_hint_y: None
    height: 40
    pos_hint: {'top': 1}
    canvas.before:
        Color:
            rgba: 0, 0, 0, .2
        RoundedRectangle:
            radius: root.roundness
            size:self.size[0], 2
            pos: self.pos
    
    BoxLayout:
        id: content
        Label:
            text: f'{root.setting}:'
            size_hint_x: .5
            text_size: self.size[0], self.text_size[1]
            halign: 'right'
            color: root.font_color
            font_size: root.height * 0.5
""")


class SettingsLine(BoxLayout, LauncherElement):

    setting = StringProperty('')
    content = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        content = self.ids['content']
        if isinstance(self.content[0], bool):
            content.add_widget(SettingsCheckbox(content=self.content[0]))
        else:
            content.add_widget(SettingsList(content=self.content[0], options=self.content[2]))

    def retrieve_data(self):
        content = self.ids['content']
        data = (self.setting, content.children[0].content)
        return data


class LauncherScreenManager(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(HomeScreen(name='home'))
        self.add_widget(SettingsScreen(name='settings'))
        self.add_widget(Screen(name='help'))


Builder.load_string("""
<LauncherUI>:
    AsyncImage:
        id: bg_image
        source: root.bg
    LauncherScreenManager:
        id: screen_manager
    Label:
        canvas.before:
            Color:
                rgba: 0, 0, 0, .2
            RoundedRectangle:
                radius: root.roundness
                size:self.size
                pos: self.pos
        text: f'Version: {root.version}' if root.version else ''
        font_size: '9pt'
        size_hint: None, None
        size: self.texture_size
        background_color: 0, 0, 0, .2
""")


class LauncherUI(RelativeLayout, LauncherElement):
    version = StringProperty('0.0.1')
    bg = StringProperty(BG_IMAGE)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        width = 1
        height=1
        Window.borderless = True
        Window.fullscreen = False
        Window.size = (width, height)
        Clock.schedule_interval(self.fetch_data, 5)
        self.setup_event = Clock.schedule_interval(self.setup_launcher, 0)
    
    def setup_launcher(self, *a):
        width = self.ids['bg_image'].texture.size[0]
        height = self.ids['bg_image'].texture.size[1]
        if height > 100 and width > 100:
            Window.size = (width, height)
            screen_width, screen_height = self.get_window_size()
            Window.top = screen_height/2 - height/2
            Window.left = screen_width/2 - width/2
            print(width, height)
            self.setup_event.cancel()

    def get_window_size(self):
        if platform.system() == 'Linux':
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