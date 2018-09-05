from kivy.properties import *
from kivy.clock import Clock

from .common import InteractiveObject
from .behavior import DamageBehavior


class Projectile(InteractiveObject, DamageBehavior):
    shooter = ObjectProperty(None)
    speed = NumericProperty(0)
    speed_max = NumericProperty(200)
    speed_max_backwards = NumericProperty(0)
    
    def on_parent(self, instance, shooter):
        self.set_initial_spos()
        
    def set_initial_spos(self):
        self.spos = self.shooter.spos
        self.angle = self.shooter.angle
        distance = self.shooter.radius + self.radius + 0.01
        self.move_foward(distance)

    def hit(self):
        self.discard = True


class Weapon:
    projectile = None
    ammunition = 0
    loaded = True
    reload_time = 0
    projectile_per_shot = 1

    def shoot(self, shooter):
        if self.loaded and self.ammunition != 0:
            self.loaded = False
            
            if self.ammunition > -1:
                self.ammunition -= self.projectile_per_shot

            if self.ammunition != 0:
                self.reload()

            return self.projectile(shooter=shooter)

    def reload(self):
        if self.reload_time:
            Clock.schedule_once(self._reload, self.reload_time)
        else:
            self.loaded = True

    def _reload(self, dt):
        self.loaded = True


class CannonBullet(Projectile):
    size_hint_x = NumericProperty(.04)
    size_hint_y = NumericProperty(.053)
    radius = NumericProperty(0.0265)
    source = StringProperty('images/cannon_bullet.png')

    speed = NumericProperty(200)
    damage = NumericProperty(70)


class Cannon(Weapon):
    projectile = CannonBullet
    reload_time = .5
    ammunition = -1