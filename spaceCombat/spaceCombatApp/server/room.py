"""SERVER"""
from threading import Thread

from kivy.clock import Clock
from kivy.properties import StringProperty

import context
from . import network
from . import game


UPDATE_PLAYERS_EVENT = None
players_update_events = []


def players_update(i):
    players = network.get_players(context.Room.room_code)
    for event in players_update_events:
        event(players)


def register_player_update_event(event):
    players_update_events.append(event)


def start_update_players():
    global UPDATE_PLAYERS_EVENT
    UPDATE_PLAYERS_EVENT = Clock.schedule_interval(players_update, 1)


def create(nickname):
    response, error = network.create_room(nickname)
    if error:
        return False, response.error_msg
    
    game.start_servers()
    start_update_players()
    return True, None


def join(room_code, nickname):
    response, error = network.join_room(room_code, nickname)
    if error:
        return False, response.error_msg

    game.start_servers()
    start_update_players()
    return True, ''


def quit():
    if context.Player:
        game.stop_servers()
        UPDATE_PLAYERS_EVENT.cancel()
        response, error = network.disconnect(context.Player.hash)

