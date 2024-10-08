import app.globals as glb

if glb.IS_PROD:
    from gevent import monkey

    monkey.patch_all()

from flask import Flask, Response, render_template
from flask_cors import CORS
from socketio import WSGIApp

from app.routes import hive_bp, track_bp, users_bp
from app.utils.library import Library
from app.utils.logger import get_logger
from app.utils.sio import sio

app = Flask(
    __name__,
    static_folder="../ui/assets",
    static_url_path="/ui/assets",
    template_folder="../ui",
)
if not glb.IS_PROD:
    cors_cfg = {"origins": glb.DEV_CLIENT}
    CORS(app, resources={r"/*": cors_cfg})
app.wsgi_app = WSGIApp(sio, app.wsgi_app)
library = Library()
logger = get_logger(__name__)


@app.route("/ui/", defaults={"subpath": ""})
@app.route("/ui/<subpath>")
def ui_routes(subpath):
    return render_template("index.html")


app.register_blueprint(track_bp)
app.register_blueprint(hive_bp)
app.register_blueprint(users_bp)


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(str(e))
    return Response(status=500)
