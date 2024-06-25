from socketio import Server
from app.utils.library import library
from app.utils.environment import env

EVENT_TRACKS = "tracks"
EVENT_NEW_USER = "new-user"
EVENT_USER_EXIT = "user-exit"


sio = Server(cors_allowed_origins=[env.DEV_CLIENT])
clients = {}


class Client:
    def __init__(self, ip, name=None, bio=None):
        self.ip = ip
        self.name = name or ip
        self.bio = bio

    def to_dict(self):
        return {"name": self.name, "bio": self.bio}


@sio.on("connect")
def connect(sid, environ, auth):
    ip = environ["REMOTE_ADDR"]
    name = auth.get("name") if auth else None
    bio = auth.get("bio") if auth else None
    client = Client(ip, name, bio)
    clients[sid] = client
    sio.emit(EVENT_NEW_USER, client.to_dict(), skip_sid=sid)


@sio.on("disconnect")
def disconnect(sid):
    client = clients[sid]
    del clients[sid]
    sio.emit(EVENT_USER_EXIT, client.to_dict())
