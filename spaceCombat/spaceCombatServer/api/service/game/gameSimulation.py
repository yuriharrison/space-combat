from kivy.clock import Clock

from ..protocolBuffer import serializer
from ..protocolBuffer import packages_pb2 as messages
from ..protocolBuffer.enums import *

from .ship import Ship


class GameSimulation:

    def __init__(self):
        self._entity_id_count = 0
        self.ships = list()
        self.projectiles = list()

    def get_next_entity_id(self):
        self._entity_id_count += 1
        return self._entity_id_count

    def start_simulation(self):
        for k, p in self.players.items():
            p.ship = Ship(id_=self.get_next_entity_id(), player_id=p.room_player_id)
            p.ship.bind(on_shoot=self.add_projectile)
            self.ships.append(p.ship)
        Clock.schedule_inderval(self.update, 1/60)# hardcoded

    def add_projectile(self, instance, projectile):
        self.projectiles.append(projectile)

    def player_ready(self, player):
        player.ready = True
        not_ready_ls = [p for k, p in self.players.items() if not p.ready]
        if not not_ready_ls:
            self.start_match()
        elif len(not_ready_ls) == 1:
            self.send_command(Commmands.EveryOneReady, host_only=True)

    def ship_update(self, player, position):
        player.ship.spos = position.x, position.y
        player.ship.angle = position.angle

    def new_action(self, player, action):
        code = Actions(action.code)
        if code == Actions.Ready:
            self.player_ready(player)
        elif code == Actions.Shoot:
            player.ship.shoot()
        elif code == Actions.NextWeapon:
            player.ship.next_weapon()
        elif code == Actions.PreviousWeapon:
            player.ship.previous_weapon()

    def update(self, dt):
        self.update_entity_list(self.ships)
        self.update_entity_list(self.projectiles)
        self.dispatch_all()

    def update_entity_list(self, entity_ls):
        for entity in entity_ls:
            if entity.discard:
                entity_ls.remove(entity)
                self.discarded_entities.append(entity)
            else:
                entity.update()

    def dispatch_all(self):
        to_dispatch_udp = list()
        for ship in self.ships:
            package = serializer.serialize(self.server_hash, PackageTypes.Ship,
                id=ship.id_,
                player_id=ship.player_id,
                x=ship.spos[0],
                y=ship.spos[1],
                angle=ship.angle,
                thruttle=ship.thruttle,
                reverse_thruttle=ship.reverse_thruttle,
                life=ship.life
            )
            to_dispatch_udp.append(package)
            
        for proj in self.projectiles:
            package = serializer.serialize(self.server_hash, PackageTypes.Projectile,
                id=proj.id_,
                x=ship.spos[0],
                y=ship.spos[1],
                angle=ship.angle,
            )
            to_dispatch_udp.append(package)

        to_dispatch_tcp = list()
        for entity in self.discarded_entities:
            package = serializer.serialize(self.server_hash, PackageTypes.Discard, 
                id=proj.id_
            )
            to_dispatch_tcp.append(package)

        for package in to_dispatch_udp:
            self.dispatch_udp(package)

        for package in to_dispatch_tcp:
            self.dispatch_tcp(package)