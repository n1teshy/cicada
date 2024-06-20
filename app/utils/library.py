import os
import glob
import hashlib
import mimetypes

from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from app.utils.environment import env
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def hash_name(name):
    hasher = hashlib.md5()
    hasher.update(name.encode("utf-8"))
    return hasher.hexdigest()


class FSEventHandler(FileSystemEventHandler):
    def __init__(self, library):
        super().__init__()
        self.library = library

    def on_created(self, event):
        self.library.add_track(event.src_path)

    def on_deleted(self, event):
        self.library.remove_track(event.src_path)


class Track:
    def __init__(self, id, file, mime, title, albums, artists, cover_id=None):
        self.id = id
        self.file = file
        self.mime = mime
        self.title = title
        self.albums = albums
        self.artists = artists
        self.cover_id = cover_id

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "albums": self.albums,
            "artists": self.artists,
            "coverId": self.cover_id,
        }


class Library:
    def __init__(self, recursive=True):
        self.tracks = {}
        pattern = "**/*" if recursive else "*"
        for file in glob.glob(
            os.path.join(env.MUSIC_FOLDER, pattern), recursive=recursive
        ):
            self.add_track(file)
        self.observer = Observer()
        self.observer.schedule(
            FSEventHandler(self), env.MUSIC_FOLDER, recursive=recursive
        )
        self.observer.start()

    def add_track(self, file):
        mime = mimetypes.guess_type(file)[0]
        if not mime or not mime.startswith("audio"):
            return None
        track_id = hash_name(file)
        title = os.path.basename(file)
        artists, almbums = [], []
        try:
            audio = MP3(file, ID3=ID3)
            title = audio.tags["TIT2"].text[0]
            artists = audio.tags["TPE1"].text
            almbums = audio.tags["TALB"].text
            # TODO: add cover image
        except:
            pass
        track = Track(track_id, file, mime, title, almbums, artists)
        self.tracks[track_id] = track
        return track

    def remove_track(self, file):
        id = hash_name(file)
        del self.tracks[id]
