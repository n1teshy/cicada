import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import get_type_hints

load_dotenv()


def folder_path(value):
    assert os.path.isdir(value), "'%s' is not a folder" % (value,)
    return os.path.abspath(value)


def file_path(value):
    assert os.path.isfile(value), "'%s' is not a file" % (value,)
    return os.path.abspath(value)


@dataclass
class Environment:
    HOST: str
    PORT: int
    MUSIC_FOLDER: folder_path
    LOG_FILE: str
    DEV_CLIENT: str
    IS_PRODUCTION: bool = False

    def __post_init__(self):
        for name, cast in get_type_hints(self).items():
            setattr(self, name, cast(getattr(self, name)))


env_vars = ["HOST", "PORT", "MUSIC_FOLDER", "LOG_FILE", "DEV_CLIENT"]
env = Environment(**{key: os.environ[key] for key in env_vars})
env.IS_PRODUCTION = os.environ["ENV"] == "PROD"
