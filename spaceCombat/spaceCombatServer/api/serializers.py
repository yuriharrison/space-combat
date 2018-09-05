from rest_framework import serializers

from .models import Player, Room


class PlayerSerializer(serializers.ModelSerializer):
    room = serializers.SlugRelatedField(read_only=True, slug_field='name')
    hash = serializers.SerializerMethodField()

    def __init__(self, instance=None, show_hash=False, **kw):
        self.show_hash = show_hash
        super().__init__(instance=None, **kw)

    def get_hash(self, obj):
        return obj.hash if self.show_hash else ''

    class Meta:
        model = Player
        fields = ('id', 'nickname', 'room_player_id', 'room', 'num_wins', 'ping', 'hash')


class RoomSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    name = serializers.ReadOnlyField()
    ports = serializers.ReadOnlyField()

    class Meta:
        model = Room
        fields = ('id', 'name', 'room_code', 'players', 'num_games', 'ports','owner')


class RoomPlayer:
    def __init__(self, room, player):
        self.room = room
        self.player = player

class RoomPlayerSerializer(serializers.Serializer):
    player = PlayerSerializer(show_hash=True)
    room = RoomSerializer()

    def __init__(self, room, player, *a, **kw):
        super().__init__(RoomPlayer(room, player), *a, **kw)
