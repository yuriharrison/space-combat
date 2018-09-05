from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view

from . import utils
from .service import services
from .models import Player, Room
from .serializers import PlayerSerializer, RoomPlayerSerializer


@api_view(['POST',])
def create_room(request, format=None):
    room_code = utils.generate_room_code()
    room = Room(room_code=room_code)
    room.ports = services.start_room(room_code)
    room.save()
    owner = room.players.create(nickname=request.data['nickname'], 
                                room_player_id=0,
                                ip_address=utils.request_ip(request))
    services.set_player(room.room_code, owner)
    services.start_ping_status(room)
    return Response(RoomPlayerSerializer(room, owner).data)


@api_view(['POST',])
def join_room(request, format=None):
    data = request.data
    try:
        nickname = data['nickname']
        room = Room.objects.get(room_code=data['room_code'])
    except KeyError:
        return Response({'error': 'nickname_required', 
                         'error_msg': 'Nickname is required.'})
    except Room.DoesNotExist:
        return Response({'error': 'invalid_code', 
                         'error_msg': 'Room code don\'t match any existing room.'})
    try:
        room.players.get(nickname=nickname)
    except Player.DoesNotExist:
        room_player_id = room.next_room_id()

        player = room.players.create(nickname=nickname, 
                                     room_player_id=room_player_id,
                                     ip_address=utils.request_ip(request))
        services.set_player(room.room_code, player)
        return Response(RoomPlayerSerializer(room, player).data)
    else:
        return Response({'error': 'invalid_nickname', 
                         'error_msg': 'Nickname already being used.'})


@api_view(['DELETE',])
def disconnect(request, hash, format=None):
    try:
        player = Player.objects.get(hash=hash)
        room = player.room
        delete_room = False
        if room.owner == player.room_player_id:
            if room.players.count() < 2:
                delete_room = True
            else:
                room.owner = room.players.first().id
                
        player.delete()
        if delete_room:
            services.close_room(room.room_code)
            room.delete()
        else:
            services.set_player(room.room_code, player, remove=True)
    except Player.DoesNotExist:
        pass

    return Response({'ok':True})


class GetPlayers(generics.ListAPIView):
    serializer_class = PlayerSerializer

    def get_queryset(self):
        return Player.objects.filter(room__room_code=self.kwargs['room_code'])


