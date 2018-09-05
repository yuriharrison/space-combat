import math

from kivy.properties import *
from kivy.lang.builder import Builder
from kivy.graphics import Rotate
from kivy.graphics.context_instructions import PushMatrix, PopMatrix
from kivy.uix.widget import Widget

from . import utils

Builder.load_string('''
<Entity>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: self._angle
            origin: self.center
    canvas.after:
        PopMatrix
''')

class EffectHandler:

    def __init__(self, **kw):
        self.effects_list = list()
        super().__init__(**kw)

    def add_effect(self, effect):
        self.effects_list.append(effect)

    def apply_effects(self):
        self.before_effects()
        self._apply_effects()
        self.after_effects()

    def _apply_effects(self):
        for effect in list(self.effects_list):
            remove = effect.update(self)
            if remove:
                self.effects_list.remove(effect)

    def before_effects(self):
        pass

    def after_effects(self):
        pass
        

class Entity(Widget, EffectHandler):
    id_ = None
    spos = ListProperty(None)
    start_angle = NumericProperty(0)
    radius = NumericProperty(None, allownone=True)
    nearby_entities = ListProperty(None, allownone=True)
    discard = BooleanProperty(False)
    _angle = NumericProperty(0)

    def __init__(self, **kw):
        self.rotation = None
        super().__init__(**kw)
        self._set_canvas()

    def on_spos(self, instance, value):
        self.pos_hint = {'center_x': value[0], 'center_y': value[1]}
        
    def _set_canvas(self):
        with self.canvas.before:
            PushMatrix()
            self.rotation = Rotate(angle=self.start_angle, origin=self.center)

        with self.canvas.after:
            PopMatrix()

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        if value < 0:
            d, mod = divmod(value, -360)
            value = 360 + mod
        else:
            d, mod = divmod(value, 360)
            value = mod

        self._angle = value
    
    @property
    def out_of_bounds(self):
        x, y = self.spos
        return x < 0 or x > 1 or y < 0 or y > 1
        
    def spos_add(self, x, y):
        xa, ya = self.spos
        self.spos = (xa + x), (ya + y)

