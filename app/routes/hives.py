from functools import wraps
from http import HTTPMethod as Method
from http import HTTPStatus as Status
from flask import request, Blueprint, Response
from app.utils.sio import clients, hives, add_hive, add_to_hive, remove_from_hive


hive_bp = Blueprint("hive", __name__)


def require_sid(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        sid = request.headers.get("Authorization")
        if sid is None:
            message = "You are not authorized"
            return {"message": message}, Status.UNAUTHORIZED
        request.sid = sid
        return f(*args, **kwargs)

    return wrapper


@hive_bp.route("/")
def hives_vf():
    return [h.to_dict() for n, h in hives.items()]


@hive_bp.route("/<string:name>/", methods=[Method.POST])
@require_sid
def hive(name):
    exists = name in hives
    if exists:
        message = f"Hive '{name}' exists already"
        return {"message": message}, Status.UNPROCESSABLE_ENTITY
    if clients[request.sid].hive is not None:
        message = "You may not join multiple hives"
        return {"message": message}, Status.FORBIDDEN
    add_hive(request.sid, name)
    return hives[name].to_dict()


@hive_bp.route("/<string:name>/join/")
@require_sid
def join_hive(name):
    if name not in hives:
        message = f"Hive '{name}' does not exist"
        return {"message": message}, Status.NOT_FOUND
    client, hive = clients[request.sid], hives[name]
    if client.hive is not None:
        message = "You may not join multiple hives"
        if client.hive is hive:
            message = f"You already are a member of '{name}'"
        return {"message": message}, Status.UNPROCESSABLE_ENTITY
    add_to_hive(request.sid, name)
    return hives[name].to_dict()


@hive_bp.route("/<string:name>/exit/")
@require_sid
def exit_hive(name):
    if name not in hives:
        message = f"Hive '{name}' does not exist"
        return {"message": message}, Status.NOT_FOUND
    client, hive = clients[request.sid], hives[name]
    if client not in hive.members:
        message = f"You may not a member of '{name}'"
        return {"message": message}, Status.UNAUTHORIZED
    remove_from_hive(request.sid, name)
    return Response()
