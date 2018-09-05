from kivy.clock import Clock
from kivy.properties import ListProperty, ObjectProperty, NumericProperty
from kivy.uix.screenmanager import Screen

import context
from game import utils
from game.ship import Ship
from game.weapons import CannonBullet
from keyboard.controller import Controller
from server import GameServer
from server.protocolBuffer.enums import *

class ServerHandler:

    def on_enter(self):
        GameServer.UDPH_INSTANCE.subscribe_many(
            ship=self._ship_update,
            projectile=self._projectile_update
        )
        GameServer.TCPH_INSTANCE.subscribe_many(
            discard=self._discard_update
        )

    def _projectile_update(self):
        for proj in self.projectiles:
            if proj.id_ == proj_info.id:
                proj.spos = (proj_info.x, proj_info.y)
                proj.angle = proj_info.angle
                return
        
        cannon_bullet = CannonBullet()
        cannon_bullet.spos = (ship_info.x, ship_info.y)
        cannon_bullet.player_id = ship_info.player_id
        cannon_bullet.angle = ship_info.angle
        self.add_projectile(cannon_bullet)

    def _ship_update(self, ship_info):
        if self.player_ship and ship_info.player_id == context.Player.room_player_id:
            return

        for ship in self.ships:
            if ship.id_ == ship_info.id:
                ship.spos = (ship_info.x, ship_info.y)
                # ship.player_id = ship_info.player_id
                ship.angle = ship_info.angle
                ship.thruttle = ship_info.thruttle
                ship.reverse_thruttle = ship_info.reverse_thruttle
                ship.life = ship.life
                return

        new_ship = Ship()
        new_ship.spos = (ship_info.x, ship_info.y)
        new_ship.player_id = ship_info.player_id
        new_ship.angle = ship_info.angle
        new_ship.thruttle = ship_info.thruttle
        new_ship.reverse_thruttle = ship_info.reverse_thruttle
        new_ship.life = ship.life
        if new_ship.player_id == context.Player.room_player_id:
            self.player_ship = new_ship
        self.add_ship(new_ship)

    def _discard_update(self, discarded):
        for proj in self.projectiles:
            if proj.id_ == discarded.id:
                self.projectiles.remove(proj)
                self.remove_widget(proj)
                return

        for ship in self.ships:
            if ship.id_ == discarded.id:
                self.ships.remove(ship)
                self.remove_widget(ship)
                return

    def send_ship(self):
        GamServer.MESSENGER_INSTANCE.send_ship(self.player_ship)

    def send_action(self, code):
        GamServer.MESSENGER_INSTANCE.send_action(code)



class ContollerHandler:

    def on_enter(self):
        self.controller = Controller(self, self._key_press_handler, 
                                     key_release_handler=self._key_release_handler)

    def _key_press_handler(self, code, key):
        if not self.player_ship:
            return

        if key == 'w':
            self.player_ship.thruttle_up()
        elif key == 's':
            self.player_ship.reverse_thruttle_up()
        elif key == 'd':
            self.player_ship.change_direction(direction='right')
        elif key == 'a':
            self.player_ship.change_direction(direction='left')

    def _key_release_handler(self, code, key):
        if not self.player_ship:
            return

        if key in ('w', 's'):
            self.player_ship.reduce_speed()
        elif key in ('a','d'):
            self.player_ship.change_direction()
        elif key == 'f':
            self.player_ship.add_effect(SlowDown())
        elif key == 'spacebar':
            self.player_ship.shoot()
            self.send_action(Actions.Shoot)

    def on_touch_down(self, touch):
        self.player_ship.spos = touch.spos

    def on_touch_move(self, touch):
        self.player_ship.spos = touch.spos


class GameScreen(Screen, ContollerHandler, ServerHandler):

    def on_enter(self):
        self.set_attributes()
        ServerHandler.on_enter(self)
        ContollerHandler.on_enter(self)
        Clock.schedule_interval(self.update, 1/60)# hardcoded

    def set_attributes(self):
        self.player_ship = None
        self.ships = list()
        self.projectiles = list()

    def on_touch_down(self, touch):
        ContollerHandler.on_touch_down(self, touch)

    def on_touch_move(self, touch):
        ContollerHandler.on_touch_move(self, touch)

    def add_ship(self, ship):
        self.add_widget(ship)
        self.ships.append(ship)

    def add_projectile(self, projectile):
        self.add_widget(projectile)
        self.projectiles.append(projectile)

    def update(self, dt):
        self.update_entity_list(self.ships)
        self.update_entity_list(self.projectiles)

    def update_entity_list(self, entity_ls):
        for entity in entity_ls:
            entity.update()
        self.send_ship()