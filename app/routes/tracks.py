import os
import re
from app import library
from http import HTTPStatus as Status
from flask import Blueprint, request, Response, send_file


track_bp = Blueprint("tracks", __name__)


@track_bp.route("/")
def tracks():
    return [library.tracks[t].to_dict() for t in library.tracks]


@track_bp.route("/<string:track_id>/")
def track(track_id):
    track = library.tracks.get(track_id)
    if track is None:
        return Response(status=Status.NOT_FOUND)
    chunk_size, size = 2 * 1024**2, os.path.getsize(track.file)
    range = request.headers.get("Range")
    if range is None:
        return send_file(track.file)
    range = re.match("bytes=(\d+)-(\d*)", range)
    if range is None:
        return Response(status=Status.BAD_REQUEST)
    start = int(range.group(1))
    end = int(range.group(2) or start + chunk_size - 1)

    def get_chunks(file, start, end):
        with open(file, "rb") as fd:
            fd.seek(start)
            while start <= end < size:
                chunk = fd.read(end - start + 1)
                yield chunk
                start += len(chunk)

    response = Response(
        get_chunks(track.file, start, end),
        status=Status.PARTIAL_CONTENT,
        content_type=track.mime,
    )
    read_size = len(response.data)
    response.headers["Content-Range"] = "bytes %d-%d/%d" % (
        start,
        start + read_size - 1,
        size,
    )
    response.headers["Accept-Ranges"] = "bytes"
    response.headers["Content-Type"] = track.mime
    response.headers["Content-Length"] = read_size
    response.headers["ETag"] = os.path.getmtime(track.file)
    response.headers["Cache-Control"] = "max-age=31536000, immutable"
    return response
