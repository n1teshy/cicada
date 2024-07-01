from socketio import Server
from app.utils.library import library
from app.utils.environment import env
from http import HTTPStatus as Status

EVENT_CONNECT = "connect"
EVENT_DISCONNECT = "disconnect"
EVENT_USER_JOIN = "user-join"
EVENT_USER_EXIT = "user-exit"
EVENT_TRACK_ADDED = "track-added"
EVENT_TRACK_REMOVED = "track-removed"
EVENT_HIVE_ADD = "add-hive"
EVENT_HIVE_REMOVE = "remove-hive"
EVENT_HIVE_MEMBER_JOIN = "hive-member-join"
EVENT_HIVE_MEMBER_EXIT = "hive-member-exit"
EVENT_PLAY_IN_HIVE = "play-in-hive"
EVENT_PAUSE_IN_HIVE = "pause-in-hive"

async_mode = "gevent" if env.IS_PRODUCTION else "threading"
sio = Server(async_mode=async_mode, cors_allowed_origins=[env.DEV_CLIENT])
library.add_track_cb = lambda track: sio.emit(EVENT_TRACK_ADDED, track.to_dict())
library.remove_track_cb = lambda track_id: sio.emit(EVENT_TRACK_REMOVED, track_id)
clients = {}
hives = {}


class Client:
    def __init__(self, sid, ip, name=None, bio=None):
        self.sid = sid
        self.name = name or ip
        self.bio = bio
        self.hive = None

    def to_dict(self):
        return {"id": self.sid, "name": self.name, "bio": self.bio}


class Hive:
    def __init__(self, name, host):
        self.name = name
        self.host = host
        self.members = set()
        self.poll = None

    def to_dict(self):
        return {
            "name": self.name,
            "host": self.host.to_dict(),
            "members": [m.to_dict() for m in self.members],
            "poll": self.poll.to_dict() if self.poll else None,
        }


@sio.on(EVENT_CONNECT)
def connect(sid, environ, auth):
    ip = environ["REMOTE_ADDR"]
    name = auth.get("name") if auth else None
    bio = auth.get("bio") if auth else None
    client = Client(sid, ip, name, bio)
    clients[sid] = client
    sio.emit(EVENT_USER_JOIN, client.to_dict(), skip_sid=sid)


@sio.on(EVENT_DISCONNECT)
def disconnect(sid):
    client = clients[sid]
    if client.hive is not None:
        remove_from_hive(sid, client.hive.name)
    del clients[sid]
    sio.emit(EVENT_USER_EXIT, client.to_dict())


@sio.on(EVENT_PLAY_IN_HIVE)
def play_in_hive(sid, data):
    client, hive = clients[sid], clients[sid].hive
    if hive is None or client is not hive.host:
        return
    if "trackId" not in data or "at" not in data:
        return
    sio.emit(EVENT_PLAY_IN_HIVE, data, room=hive.name)


@sio.on(EVENT_PAUSE_IN_HIVE)
def pause_in_hive(sid):
    client, hive = clients[sid], clients[sid].hive
    if hive is None or client is not hive.host:
        return
    sio.emit(EVENT_PAUSE_IN_HIVE, room=hive.name)


def add_hive(sid, name):
    hive = Hive(name, clients[sid])
    clients[sid].hive = hive
    hive.host = clients[sid]
    hives[name] = hive
    hive.members.add(clients[sid])
    sio.emit(EVENT_HIVE_ADD, hive.to_dict(), skip_sid=sid)
    sio.enter_room(sid, name)


def add_to_hive(sid, name):
    client, hive = clients[sid], hives[name]
    client.hive = hive
    hive.members.add(client)
    sio.emit(EVENT_HIVE_MEMBER_JOIN, client.to_dict(), room=name)
    sio.enter_room(sid, name)


def remove_from_hive(sid, name):
    client, hive = clients[sid], hives[name]
    if client is hive.host:
        print("client is host, removing the hive")
        sio.emit(EVENT_HIVE_REMOVE, name)
        for member in hives[name].members:
            member.hive = None
            sio.leave_room(member.sid, name)
        del hives[name]
        return
    client.hive = None
    hive.members.remove(client)
    sio.leave_room(sid, name)
    sio.emit(EVENT_HIVE_MEMBER_EXIT, client.to_dict(), to=name)
