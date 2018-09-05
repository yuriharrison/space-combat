from kivy.properties import *

from . import utils


class Behavior:

    def update(self):
        self.apply_effects()


class CollisionDetectionBehavior(Behavior):

    def __init__(self, **kw):
        self._collision_ls = list()
        self.register_event_type('on_collision')
        super().__init__(**kw)

    def update(self):
        self.test_collision_nearby()
        super().update()

    def on_collision(self, entity, kind):
        pass

    def test_collision_nearby(self):
        if self.nearby_entities:
            for entity in self.nearby_entities:
                self.test_collision(entity)

    def test_collision(self, entity):
        kind = None
        
        if self.radius and entity.radius and utils.circle_collision(self, entity):
            kind = 'circle'
        if utils.rectangle_collision(self, entity):
            if kind:
                kind = 'both'
            else:
                kind = 'rectangle'

        if kind and entity.id_ not in self._collision_ls:
            self.dispatch('on_collision', entity, kind)
            self._collision_ls.append(entity.id_)
        elif not kind and entity.id_ in self._collision_ls:
            self._collision_ls.remove(entity.id_)
            
            
class MovableBehavior(Behavior):
    pace = NumericProperty(.00005)
    speed = NumericProperty(0)
    speed_max = NumericProperty(100)
    speed_max_backwards = NumericProperty(-100)
    front_angle_adjust = NumericProperty(90)

    def on_speed(self, instance, value):
        if self.speed > self.speed_max:
            self.speed = self.speed_max
        elif self.speed < self.speed_max_backwards:
            self.speed = self.speed_max_backwards

    def move_foward(self, distance):
        angle = self.angle + self.front_angle_adjust
        spos = [float(i) for i in utils.coordinates(distance, angle)]
        self.spos_add(*spos)

    def update(self):
        distance = self.pace*self.speed
        self.move_foward(distance)
        super().update()


class DamageBehavior(Behavior):
    damage = NumericProperty(0)

    def hit(self, entity):
        pass


class DamageableBehavior(Behavior):
    life = NumericProperty(100)

    def __init__(self, **kw):
        self.bind(on_collision=self._on_collision)
        super().__init__(**kw)

    def _on_collision(self, i, entity, kind):
        if isinstance(entity, DamageBehavior):
            entity.hit(entity)
            self.before_damage()
            self.apply_damage(entity)
            self.after_damage()

    def apply_damage(self, entity):
        self.life -= entity.damage

    def before_damage(self):
        pass

    def after_damage(self):
        pass

    @property
    def is_alive(self):
        return self.life > 0


class ShooterBehavior(Behavior):
    current_weapon = NumericProperty(None, allownone=True)
    weapons = ListProperty(None, allownone=True)

    def __init__(self, **kw):
        self.register_event_type('on_shoot')
        super().__init__(**kw)

    def shoot(self):
        if self.current_weapon is not None:
            projectile = self.weapons[self.current_weapon].shoot(self)
            if projectile:
                self.dispatch('on_shoot', projectile)

    def on_shoot(self, projectile):
        pass

    def add_weapon(self, weapon):
        if not self.weapons:
            self.current_weapon = 0
        self.weapons.append(weapon)

    def remove_weapon(self, weapon):
        self.weapons.remove(weapon)

    def next_weapon(self):
        if self.current_weapon == len(self.weapons):
            self.current_weapon = 0
        else:
            self.current_weapon += 1

    def previous_weapon(self):
        if self.current_weapon == 0:
            self.current_weapon = len(self.weapons)
        else:
            self.current_weapon -= 1

