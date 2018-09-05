from . import packages_pb2
from .enums import PackageTypes

def serialize(hash, type_, **kw):
    message = get_message(type_)
    msg_data = message(**kw).SerializeToString()
    return packages_pb2.Package(hash=hash, type=type_.value, data=msg_data).SerializeToString()


def bytes_to_package(data):
    return packages_pb2.Package().FromString(data)


def deserialize(data):
    package = bytes_to_package(data)
    message = get_message(PackageTypes(package.type))
    message_obj = message().FromString(package.data)
    return package, message_obj


def get_message(type_):
    if type_ == PackageTypes.Command:
        return packages_pb2.Command
    if type_ == PackageTypes.Ship:
        return packages_pb2.Ship
    elif type_ == PackageTypes.Projectile:
        return packages_pb2.Projectile
    elif type_ == PackageTypes.Action:
        return packages_pb2.Action
    elif type_ == PackageTypes.Discard:
        return packages_pb2.Discard