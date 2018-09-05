from kivy.properties import *
from kivy.uix.image import Image

from .entity import Entity
from .behavior import MovableBehavior, CollisionDetectionBehavior


class Sprite(Image):
    atlas_prefix = 'atlas://'
    atlas = StringProperty(None, allownone=True)
    state = NumericProperty(None, allownone=True)
    atlas_keys = ListProperty(None, allownone=True)
    update_state = BooleanProperty(False)

    def on_atlas(self, instance, value):
        if not value.startswith(self.atlas_prefix):
            self._atlas = self.atlas_prefix + value
        else:
            self._atlas = value
            
    def on_state(self, instance, value):
        self._update_state()

    def _update_state(self):
        if self.update_state:
            self.source = self.self._atlas + self.atlas_keys[self.state]
                

class InteractiveObject(Entity, Sprite, MovableBehavior, CollisionDetectionBehavior):
    pass

