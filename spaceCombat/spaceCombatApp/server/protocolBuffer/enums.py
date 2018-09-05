from enum import Enum


class PackageTypes(Enum):
    Command = 0
    Ship = 1
    Projectile = 2
    Action = -1
    Discard = -2


class Commmands(Enum):
    StartGame = 1
    EveryOneReady = 2


class Actions(Enum):
    Ready = 0
    Shoot = 1
    NextWeapon = 2
    PreviousWeapon = 3
