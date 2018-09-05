import hashlib
import random

from django.db import models

    
class Room(models.Model):
    room_code = models.CharField(max_length=6, unique=True)
    num_games = models.IntegerField(default=0)
    port_tcp = models.IntegerField()
    port_udp = models.IntegerField()
    owner = models.IntegerField(default=0)
    
    @property
    def name(self):
        try:
            owner = self.players.get(room_player_id=self.owner)
            owner_nick_name = owner.nickname
        except Player.DoesNotExist:
            owner_nick_name = 'Nobody'
        return '{}\'s room - {}'.format(owner_nick_name, self.room_code)

    @property
    def ports(self):
        return self.port_tcp, self.port_udp

    @ports.setter
    def ports(self, value):
        self.port_tcp, self.port_udp = value

    def next_room_id(self):
        last_id = self.players.order_by('-room_player_id').first().room_player_id
        return last_id + 1


class Player(models.Model):
    nickname = models.CharField(max_length=100, blank=False)
    ip_address = models.CharField(max_length=11)
    room_player_id = models.IntegerField()
    room = models.ForeignKey(Room, related_name='players', on_delete=models.CASCADE)
    num_wins = models.IntegerField(default=0)
    hash = models.CharField(max_length=20, blank=False)
    ping = models.CharField(max_length=5, default='999ms')

    def save(self, *a, **kw):
        if not self.hash:
            self.hash = self.gen_hash()
        super().save(*a, **kw)

    def gen_hash(self):
        to_hash = self.nickname + str(random.randint(99,99999))
        return hashlib.sha1(to_hash.encode()).hexdigest()

    class Meta:
        ordering = ('room_player_id',)