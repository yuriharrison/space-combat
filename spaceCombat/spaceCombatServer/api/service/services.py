"""API SERVICE"""
import os
import time
import random
import hashlib
from threading import Thread

from .protocolBuffer import serializer, packages_pb2
from .protocolBuffer.enums import *
from ..models import Room
from .easysocket import TCPServer, UDPServer, TCPClient, UDPClient
from .game.gameSimulation import GameSimulation

ROOM_SERVERS = dict()
SERVER_IP = '192.168.0.6'


def get_ping(ip_address):
    ping = os.popen('ping {} -n 1'.format(ip_address))
    result = ping.readlines()
    msLine = result[-1].strip()
    text = msLine.split(' = ')[-1]
    return text if text.endswith('ms') else '999ms'


def start_ping_status(room):
    def loop(room_id):
        while True:
            # ip_list = ['www.google.com', 'www.facebook.com', 'www.yahoo.com', 'www.youtube.com', 'www.twitter.com']
            try:
                room = Room.objects.get(id=room_id)
            except Room.DoesNotExist:
                break
            else:
                try:
                    for p in room.players.all():
                        p.ping = get_ping(p.ip_address)
                        p.save()
                except Exception as ex:
                    pass
                finally:
                    time.sleep(10)
    Thread(target=loop, args=(room.id,)).start()


def start_room(room_code):
    ROOM_SERVERS[room_code] = room = RoomServer(room_code)
    return room.ports

def set_player(room_code, player, remove=False):
    if remove:
        ROOM_SERVERS[room_code].remove_player(player)
    else:
        ROOM_SERVERS[room_code].add_player(player)

def close_room(room_code):
    ROOM_SERVERS[room_code].close()
    

class RoomServer(GameSimulation):
    PORTS_BEING_USED = []
    PLAYERS_DEFAULT_TCP_PORT = 54970
    PLAYERS_DEFAULT_UDP_PORT = 54971

    def __init__(self, room_code):
        self.room_code = room_code
        self.start()
        super().__init__()

    def start(self):
        self.players = dict()
        self.room = None
        self.ports = tcp_port, udp_port = self._generate_ports()
        self.tcp_server = TCPHandler(SERVER_IP, tcp_port, self._tcp_handler)
        self.udp_server = UDPHandler(SERVER_IP, udp_port, self._udp_handler)
        Thread(target=self.tcp_server.serve_forever).start()
        Thread(target=self.udp_server.serve_forever).start()

    def add_player(self, player):
        player.server_tcp = (player.ip_address, self.PLAYERS_DEFAULT_TCP_PORT)
        player.server_udp = (player.ip_address, self.PLAYERS_DEFAULT_UDP_PORT)
        player.hash_enc = player.hash.encode()
        player.ready = False
        self.players[player.hash_enc] = player

        if not self.room:
            self.room = Room.objects.get(room_code=self.room_code)

        if player.room_player_id == self.room.owner:
            self.host = player

    def remove_player(self, player):
        del self.players[player.hash.encode()]

    def start_match(self):
        self.start_simulation()
        self.send_command(Commmands.StartGame)

    def close(self):
        self.tcp_server.stop_serve()
        self.udp_server.stop_serve()
        self.players = dict()

    def _generate_ports(self):
        tcp_port = None
        udp_port = None

        while not tcp_port or tcp_port in RoomServer.PORTS_BEING_USED:
            tcp_port = random.randint(9999, 59999)

        while not udp_port or udp_port in RoomServer.PORTS_BEING_USED:
            udp_port = random.randint(9999, 59999)

        RoomServer.PORTS_BEING_USED.append(tcp_port)
        RoomServer.PORTS_BEING_USED.append(udp_port)
        return tcp_port, udp_port


    def _tcp_handler(self, data):
        package, message = serializer.deserialize(data)
        from_ = self.players[package.hash]
        type_ = PackageTypes(package.type)
        if type_ == PackageTypes.Action:
            self.new_action(from_, message)

    def _udp_handler(self, data):
        package, message = serializer.deserialize(data)
        from_ = self.players[package.hash]
        type_ = PackageTypes(package.type)
        if type_ == PackageTypes.Ship:
            self.ship_update(from_, message)

    def send_command(self, code, host_only=False):
        data = serializer.serialize(self.room.room_code.encode(), PackageTypes.Command, code=code.value)
        if host_only:
            self._send_tcp(*self.host.server_tcp, data)
        else:
            self._dispatch_tcp(data)

    def dispatch_tcp(self, data):
        for k, p in self.players.items():
            self._send_tcp(*p.server_tcp, data)

    def _send_tcp(self, ip, port, data):
        TCPClient(ip, port).send_all(data)
            
    def dispatch_udp(self, data): # from_, 
        # for p in self._receivers(from_):
        #     UDPClient(*p.server_udp).send(data)
        for k, p in self.players.items():
            self._send_udp(*p.server_udp, data)

    def _send_udp(self, ip, port, data):
        UDPClient(ip, port).send(data)

    # def _receivers(self, from_):
    #     for hash_ in self.players:
    #         if hash_ == from_.hash_enc:
    #             continue
    #         yield self.players[hash_]


class Handler:

    def __init__(self, server, port, func):
        self.func = func
        super().__init__(server, port)


class TCPHandler(Handler, TCPServer):

    def receive_all(self, data):
        self.func(data)
    

class UDPHandler(Handler, UDPServer):

    def receive(self, addr, data):
        self.func(data)