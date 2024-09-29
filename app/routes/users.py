from http import HTTPMethod as Method

from flask import Blueprint, request, Response
from app.utils.sio import update_user_info

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("/<string:sid>/", methods=[Method.PUT])
def user(sid):
    name, bio = request.json["name"], request.json["bio"]
    update_user_info(sid, name, bio)
    return Response()
