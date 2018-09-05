from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen

import context
from screens import GameScreen
from server import RoomServer, GameServer
from customWidgets.selectionBox import SelectionBox, SelectionBoxItem

Builder.load_file('main.kv')

class PlayerDisplay(SelectionBoxItem):
    pass

class RoomScreen(Screen):
    room_name = StringProperty('Room Name')
    room_code = StringProperty('999.999.99.99')
    everyone_ready = BooleanProperty(False)
    is_host = BooleanProperty(False)

    def on_enter(self):
        RoomServer.register_player_update_event(self.players_update)
        GameServer.TCPH_INSTANCE.subscribe_many(
            start_match=self.start_match,
            everyone_ready=self.everyone_ready_update
        )
        self.room_name = context.Room.name
        self.room_code = context.Room.room_code
        self.is_host = context.Room.owner == context.Player.room_player_id
        self.ids.btn_ready.disabled = self.is_host
        self.ids.btn_ready.text = 'Ready' if not self.is_host else 'Wait'


    def players_update(self, players):
        self.ids.sb_players.clean()
        self.ids.sb_players.data = players
        self.ids.sb_players.load_items()

    def everyone_ready_update(self):
        self.everyone_ready = True
        self.ids.btn_ready.disabled = False
        self.ids.btn_ready.text = 'Start'

    def start_match(self):
        self.manager.current = self.manager.game_screen.name

    def ready(self):
        GameServer.MESSENGER_INSTANCE.ready_to_play()
        self.ids.btn_ready.disabled = True
        self.ids.btn_ready.text = 'Wait'

    def quit_room(self):
        RoomServer.quit()
        self.manager.current = self.manager.main_menu_screen.name


class MainMenuScreen(Screen):
    nickname = StringProperty(None, allownone=True)
    room_code = StringProperty(None, allownone=True)
    nickname_error = StringProperty('')

    def on_leave(self):
        self.nickname_error = ''
        self.ids.room_code_msg.state = ''

    def join_room(self):
        if not self.validate():
            return

        self.ids.room_code.state = 'connecting'
        conn, error = RoomServer.join(self.room_code, self.nickname)
        if conn:
            self.go_to_room()
        else:
            self.ids.room_code_msg.state = 'error'
            self.ids.room_code_msg.text = error

    def validate(self):
        valid = True
        if not self.nickname:
            self.nickname_error = 'Nickname can\'t be empty.'
            valid = False

        if not self.room_code:
            self.ids.room_code_msg.state = 'error'
            self.ids.room_code_msg.text = 'Room IP is required.'
            valid = False

        return valid

    def host(self):
        # TODO: handle error
        RoomServer.create(self.nickname)
        self.go_to_room()

    def go_to_room(self):
        self.manager.current = self.manager.room_screen.name


class MainApp(App):
    debug_game = False

    def build(self):
        sm = ScreenManager()
        if self.debug_game:
            sm.current = sm.game_screen.name
        return sm

    def on_stop(self):
        RoomServer.quit()


if __name__ == '__main__':
    MainApp().run()