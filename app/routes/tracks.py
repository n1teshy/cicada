import os
import re
from app import library
from http import HTTPStatus as Status
from flask import Blueprint, request, Response


track_bp = Blueprint("tracks", __name__)


@track_bp.route("/")
def tracks():
    return [library.tracks[t].to_dict() for t in library.tracks]


@track_bp.route("/<string:track_id>/")
def track(track_id):
    track = library.tracks.get(track_id, None)
    if track is None:
        return Response()
    chunk_size, size = 1024 * 1024, os.path.getsize(track.file)
    range = re.match(
        "bytes=(\d+)-(\d*)", request.headers.get("Range", f"bytes=0-{chunk_size-1}")
    )
    start, end = int(range.group(1) or 0), int(range.group(2) or size - 1)

    def get_chunks(start, end):
        with open(track.file, "rb") as fd:
            fd.seek(start)
            while chunk := fd.read(min(chunk_size, end - start + 1)):
                yield chunk

    readable_size = min(chunk_size, end - start + 1)
    response = Response(
        get_chunks(start, start + readable_size - 1),
        status=Status.PARTIAL_CONTENT,
        content_type=track.mime,
    )
    response.headers["Content-Range"] = "bytes %d-%d/%d" % (
        start,
        start + readable_size - 1,
        size,
    )
    response.headers["Accept-Ranges"] = "bytes"
    response.headers["Content-Type"] = track.mime
    response.headers["Content-Length"] = readable_size
    start += readable_size
    return response
