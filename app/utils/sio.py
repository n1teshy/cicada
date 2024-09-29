import socket

from socketio import Server

import app.globals as glb
from app.utils.library import library

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
EVENT_SPEAK_TO_HIVE = "speak-to-hive"
EVENT_PLAY_IN_HIVE = "play-in-hive"
EVENT_PAUSE_IN_HIVE = "pause-in-hive"
EVENT_HIVE_TRACK_SYN = "hive-track-syn"
EVENT_HIVE_TRACK_ACK = "hive-track-ack"

sio_params = {"async_mode": "gevent" if glb.IS_PROD else "threading"}
if not glb.IS_PROD:
    sio_params["cors_allowed_origins"] = [glb.DEV_CLIENT]
sio = Server(**sio_params)
library.add_track_cb = lambda track: sio.emit(EVENT_TRACK_ADDED, track.to_dict())
library.remove_track_cb = lambda track_id: sio.emit(EVENT_TRACK_REMOVED, track_id)
users = {}
hives = {}


class User:
    def __init__(self, sid, name, bio=None):
        self.sid = sid
        self.name = name
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
    if not name:
        try:
            hostname, _, __ = socket.gethostbyaddr(ip)
            name = hostname
        except OSError:
            pass
    if not name:
        name = ip
    bio = auth.get("bio") if auth else None
    user = User(sid, name, bio)
    users[sid] = user
    sio.emit(EVENT_USER_JOIN, user.to_dict(), skip_sid=sid)


@sio.on(EVENT_DISCONNECT)
def disconnect(sid):
    user = users[sid]
    if user.hive is not None:
        remove_from_hive(sid, user.hive.name)
    del users[sid]
    sio.emit(EVENT_USER_EXIT, user.to_dict())


@sio.on(EVENT_PLAY_IN_HIVE)
def play_in_hive(sid, data):
    user, hive = users[sid], users[sid].hive
    if hive is None or user is not hive.host:
        return
    if "trackId" not in data or "at" not in data:
        return
    sio.emit(EVENT_PLAY_IN_HIVE, data, room=hive.name)


@sio.on(EVENT_PAUSE_IN_HIVE)
def pause_in_hive(sid):
    user, hive = users[sid], users[sid].hive
    if hive is None or user is not hive.host:
        return
    sio.emit(EVENT_PAUSE_IN_HIVE, room=hive.name)


@sio.on(EVENT_HIVE_TRACK_SYN)
def hive_track_syn(sid, trackId):
    user = users[sid]
    if user.hive is None or user.hive.host is not user:
        return
    sio.emit(EVENT_HIVE_TRACK_SYN, trackId, room=user.hive.name)


@sio.on(EVENT_HIVE_TRACK_ACK)
def hive_track_ack(sid, trackId):
    user = users[sid]
    if user.hive is None:
        return
    sio.emit(EVENT_HIVE_TRACK_ACK, trackId, room=user.hive.name)


@sio.on(EVENT_SPEAK_TO_HIVE)
def speak_to_hive(sid, message):
    user, hive = users[sid], users[sid].hive
    if hive is None:
        return
    data = {"speaker": user.to_dict(), "message": message}
    sio.emit(EVENT_SPEAK_TO_HIVE, data, room=hive.name)


def add_hive(sid, name):
    hive = Hive(name, users[sid])
    users[sid].hive = hive
    hive.host = users[sid]
    hives[name] = hive
    hive.members.add(users[sid])
    sio.emit(EVENT_HIVE_ADD, hive.to_dict(), skip_sid=sid)
    sio.enter_room(sid, name)


def add_to_hive(sid, name):
    user, hive = users[sid], hives[name]
    user.hive = hive
    hive.members.add(user)
    sio.emit(EVENT_HIVE_MEMBER_JOIN, user.to_dict(), room=name)
    sio.enter_room(sid, name)


def remove_from_hive(sid, name):
    user, hive = users[sid], hives[name]
    if user is hive.host:
        sio.emit(EVENT_HIVE_REMOVE, name)
        for member in hives[name].members:
            member.hive = None
            sio.leave_room(member.sid, name)
        del hives[name]
        return
    user.hive = None
    hive.members.remove(user)
    sio.leave_room(sid, name)
    sio.emit(EVENT_HIVE_MEMBER_EXIT, user.to_dict(), to=name)


def update_user_info(sid, name, bio):
    user = users[sid]
    user.name, user.bio = name, bio
