from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.popup import Popup

Builder.load_string('''
<MessagePopup>:
    size_hint: .8,.8

    BoxLayout:
        orientation: 'vertical'

        Label:
            text: root.message
            text_size: self.size
            padding_y: sp(20)
            halign: 'left'
            valign: 'top'
''')


class MessagePopup(Popup):
    message = StringProperty(None)
