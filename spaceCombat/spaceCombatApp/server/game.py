from threading import Thread

import context
from . import network
from .easysocket import TCPServer, UDPServer
from .protocolBuffer import packages_pb2, serializer
from .protocolBuffer.enums import *


TCPH_INSTANCE = None
UDPH_INSTANCE = None
MESSENGER_INSTANCE = None


def start_servers():
    global TCPH_INSTANCE, UDPH_INSTANCE, MESSENGER_INSTANCE
    TCPH_INSTANCE, UDPH_INSTANCE = network.start_servers(TCPHandler, UDPHandler)
    Thread(target=TCPH_INSTANCE.serve_forever, name='tcp_server').start()
    Thread(target=UDPH_INSTANCE.serve_forever, name='udp_server').start()
    MESSENGER_INSTANCE = Messenger(context.Player.hash)


def stop_servers():
    global TCPH_INSTANCE, UDPH_INSTANCE, MESSENGER_INSTANCE
    TCPH_INSTANCE.stop_serve()
    UDPH_INSTANCE.stop_serve()
    TCPH_INSTANCE = None
    UDPH_INSTANCE = None
    MESSENGER_INSTANCE = None


class Messenger:

    def  __init__(self, hash):
        self.hash = hash.encode()

    def send_ship(self, ship):
        package_data = serializer.serialize(self.hash, PackageTypes.Ship,
            id=ship.id_,
            player_id=ship.player_id,
            x=ship.spos[0],
            y=ship.spos[1],
            angle=ship.angle,
            thruttle=ship.thruttle,
            reverse_thruttle=ship.reverse_thruttle,
            life=ship.life
        )
        network.send_udp(package_data)

    def send_action(self, code):
        package_data = serializer.serialize(self.hash, PackageTypes.Action, code=code.value)
        network.send_tcp(package_data)

    def ready_to_play(self):
        self.send_action(Actions.Ready)

    
class Observable:
    _events = dict()

    def subscribe(self, event, func):
        events = self._events
        if event in events:
            events[event].append(func)
        else:
            events[event] = [func,]

    def subscribe_many(self, **kw):
        for key, value in kw.items():
            self.subscribe(key, value)

    def unsubscribe(self, event, func):
        self._events[event].remove(func)

    def update(self, event, **kw):
        for func in self._events[event]:
            func(**kw)


class TCPHandler(TCPServer, Observable):
    
    def receive_all(self, data):
        package, message = serializer.deserialize(data)
        type_ = PackageTypes(package.type)
        if type_ == PackageTypes.Command:
            code = Commmands(message.code)
            if code == Commmands.StartGame:
                self.update('start_match')
            elif code == Commmands.EveryOneReady:
                self.update('everyone_ready')
        elif type_ == PackageTypes.Discard:
            self.update('discard', discarded=message)


class UDPHandler(UDPServer, Observable):
    
    def receive(self, addr, data):
        package, message = serializer.deserialize(data)

        if package.type == 1:
            self.update('ship', ship=message)
        elif package.type == 2:
            self.update('projectile', projectile=message)