"""KEYBOARD CONTROLLER"""
from threading import Thread
from kivy.core.window import Window
from .rateLimitDecorator import RateLimited

class Controller:
    
    def __init__(self, widget, key_press_handler, key_release_handler=None):
        self.widget = widget
        self.key_press_handler = key_press_handler
        self.key_release_handler = key_release_handler
        self.keys_being_pressed = dict()
        self.kill_thread = False

        self._thread = Thread(target=self._seeder)
        self._thread.start()

        self._bind_keyboard()

    def _bind_keyboard(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self.widget)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, *i):
        self.keys_being_pressed[keycode[0]] = keycode[1]
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        self.keys_being_pressed.pop(keycode[0])
        self.key_release_handler(*keycode)
        return True

    def _seeder(self):
        @RateLimited(61)
        def _seed(self):
            for key, value in dict(self.keys_being_pressed).items():
                self.key_press_handler(key, value)

        while not self.kill_thread:
            _seed(self)