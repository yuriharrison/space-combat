import time
import traceback

from kivy.properties import *
from kivy.event import EventDispatcher

# TODO: Implement stack handler

class Effect(EventDispatcher):
    duration = NumericProperty(None)
    power = NumericProperty(1)
    permanent = BooleanProperty(False)
    _start_time = NumericProperty(None, allownone=True)

    def __init__(self, duration=None, power=1):
        self.duration = duration
        self.power = power
        self.permanent = not duration

    def update(self, entity):
        pass

    def time_out(self):
        if self.permanent:
            return False

        if self._start_time and self.duration < (time.time() - self._start_time):
            return True
        elif not self._start_time:
            self._start_time = time.time()
            return False


class FrameEffect(Effect):
    
    def __init__(self, effect, **kw):
        self._effect = effect
        super().__init__(**kw)

    def update(self, entity):
        if self.time_out():
            return True

        try:
            stop = self._effect(entity)
            if stop:
                return True
        except:
            traceback.print_exc()
            return True


class ApplyAndFadeEffect(Effect):
    applied = BooleanProperty(False)

    def update(self, entity):
        try:
            if not self.applied:
                stop = None
                self.apply(entity)
                self.applied = True
                    
            if self.time_out():
                self.fade(entity)
                return True
        except:
            traceback.print_exc()
            return True

    def apply(self, entity):
        pass

    def fade(self, entity):
        pass


class GenericEffect(ApplyAndFadeEffect):
    
    def __init__(self, apply, fade):
        self.apply = apply
        self.fade = fade
        super().__init__(**kw)


class SlowDown(ApplyAndFadeEffect):
    
    def __init__(self, penalty=.5, duration=.5, **kw):
        self.penalty = penalty
        super().__init__(duration=duration, **kw)

    def apply(self, entity):
        self._original_speed_max = entity.speed_max
        entity.speed_max = self._original_speed_max * self.penalty / self.power

    def fade(self, entity):
        entity.speed_max = self._original_speed_max
        

class ScreenBoundariesTeleport(FrameEffect):

    def __init__(self):
        super().__init__(self.effect)
    
    def effect(self, entity):
        x, y = entity.spos
        if x > 1:
            x -= 1
        elif x < 0:
            x = 1 + x
        if y > 1:
            y -= 1
        elif y < 0:
            y = 1 + y

        entity.spos = x,y
