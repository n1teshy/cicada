import argparse
import sys
from pathlib import Path

import app.globals as glb

program = argparse.ArgumentParser(
    formatter_class=lambda prog: argparse.HelpFormatter(
        prog, max_help_position=100
    )
)
program.add_argument(
    "host", help="the address to host the app on, e.g. 0.0.0.0"
)
program.add_argument(
    "port", type=int, help="the port to serve the app on, e.g. 8080"
)
program.add_argument(
    "music_dir", type=Path, help="the folder with the audio files"
)
program.add_argument("--log", type=Path, help="log file")
# for UI development, probably won't be used by people other than developers
program.add_argument(
    "--dev", action="store_true", help="run in development mode"
)
program.add_argument("--client", help="UI client")


if __name__ == "__main__":
    args = program.parse_args(sys.argv[1:] or ["-h"])
    assert args.dev == (
        args.client is not None
    ), "specify the client in development mode"
    glb.HOST, glb.PORT = args.host, args.port
    glb.MUSIC_DIR, glb.LOG_FILE = args.music_dir, args.log
    glb.IS_PROD, glb.DEV_CLIENT = not args.dev, args.client

    from app.init import app
    from app.utils.logger import get_logger

    logger = get_logger(__name__)

    if glb.IS_PROD:
        from gevent.pywsgi import WSGIServer

        server = WSGIServer((glb.HOST, glb.PORT), app)
        logger.info("serving music at %s:%d" % (glb.HOST, glb.PORT))
        server.serve_forever()
    else:
        app.run(host=glb.HOST, port=glb.PORT, debug=True)
