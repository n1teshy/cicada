import importlib

from app import app
from app.utils.environment import env
from app.utils.logger import get_logger

logger = get_logger(__name__)


if env.IS_PRODUCTION:
    waitress = importlib.import_module("waitress")
    logger.info("serving music at %s:%d" % (env.HOST, env.PORT))
    waitress.serve(app, host=env.HOST, port=env.PORT, threads=env.WAITRESS_THREADS)
else:
    app.run(host=env.HOST, port=env.PORT, debug=True)
