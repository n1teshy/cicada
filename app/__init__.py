from app.utils.environment import env

if env.IS_PRODUCTION:
    from gevent import monkey

    monkey.patch_all()

from flask_cors import CORS
from socketio import WSGIApp
from app.utils.sio import sio
from app.utils.library import Library
from app.utils.logger import get_logger
from flask import Flask, render_template, Response


app = Flask(
    __name__,
    static_folder="../dist/assets",
    static_url_path="/ui/assets",
    template_folder="../dist",
)
cors = CORS(app, resources={r"/*": {"origins": env.DEV_CLIENT}})
app.wsgi_app = WSGIApp(sio, app.wsgi_app)
library = Library()
logger = get_logger(__name__)


@app.route("/ui/", defaults={"subpath": ""})
@app.route("/ui/<subpath>")
def ui_routes(subpath):
    return render_template("index.html")


# add '/api/track/*' endpoints
from app.routes.tracks import track_bp
from app.routes.hives import hive_bp

app.register_blueprint(track_bp, url_prefix="/api/tracks")
app.register_blueprint(hive_bp, url_prefix="/api/hives")


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(str(e))
    return Response(status=500)
