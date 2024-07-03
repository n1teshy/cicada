import os
import glob
import hashlib
import mimetypes

from mutagen import File
from app.utils.environment import env
from app.utils.logger import get_logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = get_logger(__name__)


def hash_name(name):
    hasher = hashlib.md5()
    hasher.update(name.encode("utf-8"))
    return hasher.hexdigest()


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


class FSEventHandler(FileSystemEventHandler):
    def __init__(self, library):
        super().__init__()
        self.library = library

    def on_created(self, event):
        self.library.add_track(event.src_path)

    def on_deleted(self, event):
        self.library.remove_track(event.src_path)


class Track:
    def __init__(self, id, file, mime, title, albums, artists, duration, cover_id=None):
        self.id = id
        self.file = file
        self.mime = mime
        self.title = title
        self.albums = albums
        self.artists = artists
        self.duration = duration
        self.cover_id = cover_id

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "albums": self.albums,
            "artists": self.artists,
            "duration": self.duration,
            "coverId": self.cover_id,
        }


def start_observer(library, recursive):
    observer = Observer()
    observer.schedule(FSEventHandler(library), env.MUSIC_FOLDER, recursive=recursive)
    observer.start()


@singleton
class Library:
    def __init__(self, recursive=True):
        self.tracks = {}
        self.add_track_cb = lambda track: None
        self.remove_track_cb = lambda track_id: None
        pattern = "**/*" if recursive else "*"
        for file in glob.glob(
            os.path.join(env.MUSIC_FOLDER, pattern), recursive=recursive
        ):
            self.add_track(file)

    def add_track(self, file):
        mime = mimetypes.guess_type(file)[0]
        if not mime or not mime.startswith("audio"):
            return None
        try:
            audio = File(file)
        except:
            logger.error(f"could not open {file}")
            return
        track_id = hash_name(file)
        title = os.path.basename(file)
        artists, almbums = [], []
        duration = audio.info.length
        try:
            title = audio.tags["TIT2"].text[0]
            artists = audio.tags["TPE1"].text
            almbums = audio.tags["TALB"].text
            # TODO: add cover image
        except:
            pass
        track = Track(track_id, file, mime, title, almbums, artists, duration)
        self.tracks[track_id] = track
        self.add_track_cb(track)

    def remove_track(self, file):
        id = hash_name(file)
        del self.tracks[id]
        self.remove_track_cb(id)


library = Library()
