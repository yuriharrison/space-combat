"""NETWORK CONNECTION"""
import slumber

import context
from .easysocket import TCPClient, UDPClient

CONNECTION = None
SERVER_ADDRESS = '192.168.0.6'
SERVER_API_PORT = 8000
API_USER = 'application'
API_PASSWORD = 'app123'
TCP_CLIENT_PORT = 54970
UDP_CLIENT_PORT = 54971
TCP_SERVER_PORT = None
UDP_SERVER_PORT = None


class DictObject:
    
    def __init__(self, data):
        self.__dict__.update(data) 


class Player(DictObject):
    pass

class Room(DictObject):
    pass

class RequestError:

    def __init__(self, error_message):
        self.error_msg = error_message


def api_url():
    return 'http://{}:{}'.format(SERVER_ADDRESS, SERVER_API_PORT)

def set_server_ports(room):
    global TCP_SERVER_PORT, UDP_SERVER_PORT
    TCP_SERVER_PORT, UDP_SERVER_PORT = room.ports

def connect_to_server():
    global CONNECTION
    CONNECTION = slumber.API(api_url())# , auth=(API_USER, API_PASSWORD))


def start_servers(tcp_handler, udp_handler):
    tcph_instance = tcp_handler(context.CURRENT_IP, TCP_CLIENT_PORT)
    udph_instance = udp_handler(context.CURRENT_IP, UDP_CLIENT_PORT)
    return tcph_instance, udph_instance


def send_tcp(data):
    server = TCPClient(SERVER_ADDRESS, TCP_SERVER_PORT)
    server.send_all(data)


def send_udp(data):
    server = UDPClient(SERVER_ADDRESS, UDP_SERVER_PORT)
    server.send(data)


def connection_error(func):
    def wrapper(*a, **kw):
        try:
            request_error = func(*a, **kw)
            if request_error:
                return request_error, True
            else:
                return None, False

        except ConnectionError:
            return RequestError('Connection Error'), True
        except slumber.exceptions.HttpServerError:
            return RequestError('Server Error'), True
        except slumber.exceptions.HttpClientError:
            return RequestError('Client Error'), True
        except:
            return RequestError('Unexpected error connecting to the server'), True
    return wrapper


@connection_error
def create_room(nickname):
    if not CONNECTION:
        connect_to_server()
    data = CONNECTION.create_room.post({'nickname': nickname})
    if 'error' in data:
        return RequestError(data['error_msg'])
    else:
        context.Room = room = Room(data['room'])
        context.Player = Player(data['player'])
        set_server_ports(room)


@connection_error
def join_room(room_code, nickname):
    if not CONNECTION:
        connect_to_server()
    data = CONNECTION.join_room.post({'room_code': room_code, 'nickname': nickname})
    if 'error' in data:
        return RequestError(data['error_msg'])
    else:
        context.Room = room = Room(data['room'])
        context.Player = Player(data['player'])
        set_server_ports(room)

@connection_error
def disconnect(player_hash):
    if not CONNECTION:
        connect_to_server()
    data = CONNECTION.disconnect(player_hash).delete()
    if 'error' in data:
        return RequestError(data['error_msg'])
    else:
        context.Room = None
        context.Player = None


def get_players(room_code):
    return [Player(data) for data in CONNECTION.players(room_code).get()]

