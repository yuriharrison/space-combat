from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.image import Image

from . import utils
from .effect import ScreenBoundariesTeleport
from .behavior import ShooterBehavior, DamageableBehavior
from .common import InteractiveObject
from .weapons import Cannon


class Ship(InteractiveObject, ShooterBehavior, DamageableBehavior):
    size_hint_x = NumericProperty(.04)
    size_hint_y = NumericProperty(.053)
    radius = NumericProperty(0.0265)
    source = StringProperty('images/ship.png')

    speed_pace = NumericProperty(1.5)
    torque = NumericProperty(.7)
    torque_backwards = NumericProperty(.35)
    thruttle = NumericProperty(0)
    thruttle_min = NumericProperty(0)
    thruttle_max = NumericProperty(1)
    reverse_thruttle = NumericProperty(0)
    reverse_thruttle_min = NumericProperty(0)
    reverse_thruttle_max = NumericProperty(1)
    direction = NumericProperty(0)
    direction_range = ListProperty((-30,30))

    player_id = NumericProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.add_effect(ScreenBoundariesTeleport())
        self.add_weapon(Cannon())

    def on_thruttle(self, instance, value):
        if self.thruttle > self.thruttle_max:
            self.thruttle = self.thruttle_max
        elif self.thruttle < self.thruttle_min:
            self.thruttle = self.thruttle_min

        if self.thruttle > self.thruttle_min:
            self.reverse_thruttle = self.reverse_thruttle_min

    def on_reverse_thruttle(self, instance, value):
        if self.reverse_thruttle > self.reverse_thruttle_max:
            self.reverse_thruttle = self.reverse_thruttle_max
        elif self.reverse_thruttle < self.reverse_thruttle_min:
            self.reverse_thruttle = self.reverse_thruttle_min

        if self.reverse_thruttle > self.reverse_thruttle_min:
            self.thruttle = self.thruttle_min

    def thruttle_up(self):
        self.thruttle = self.thruttle_max

    def thruttle_down(self):
        self.thruttle = self.thruttle_min

    def move_thruttle(self, rise=None, lower=None, set_=None):
        if rise:
            self.thruttle += rise
        elif lower:
            self.thruttle -= lower
        elif set_:
            self.thruttle = set_

    def reverse_thruttle_up(self):
        self.reverse_thruttle = self.reverse_thruttle_max

    def reverse_thruttle_down(self):
        self.reverse_thruttle = self.reverse_thruttle_min

    def move_reverse_thruttle(self, rise=None, lower=None, set_=None):
        if rise:
            self.reverse_thruttle += rise
        elif lower:
            self.reverse_thruttle -= lower
        elif set_:
            self.reverse_thruttle = set_

    def change_direction(self, direction=None):
        right, left = self.direction_range
        if direction == 'left':
            self.direction = left
        elif direction == 'right':
            self.direction = right
        else:
            self.direction = 0

    def reduce_speed(self):
        if self.speed < 0:
            self.move_thruttle(set_=.2)
        elif self.speed > 0:
            self.move_reverse_thruttle(set_=.2)

    def update_speed(self):
        if self.thruttle:
            self.speed += self.thruttle * self.torque * self.speed_pace
        elif self.reverse_thruttle:
            self.speed -= self.reverse_thruttle * self.torque_backwards * self.speed_pace

    def update_angle(self):
        self.angle += self.direction/30

    def update(self):
        self.update_speed()
        self.update_angle()
        super().update()