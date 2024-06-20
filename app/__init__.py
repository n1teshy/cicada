import socketio

from app.utils.library import Library
from app.utils.logger import get_logger
from flask import Flask, render_template, Response


app = Flask(__name__)
sio = socketio.Server()
app = socketio.WSGIApp(sio, app)
library = Library()
logger = get_logger(__name__)


from app.routes.tracks import track_bp

app = Flask(
    __name__,
    static_folder="../dist/assets",
    static_url_path="/ui/assets",
    template_folder="../dist",
)


@app.route("/ui/", defaults={"subpath": ""})
@app.route("/ui/<subpath>")
def ui_routes(subpath):
    return render_template("index.html")


app.register_blueprint(track_bp, url_prefix="/api/tracks")


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(str(e))
    return Response(status=500)
