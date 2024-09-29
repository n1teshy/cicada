from app.routes.hives import hive_bp
from app.routes.tracks import track_bp
from app.routes.users import users_bp

# Adding this so the linter doesn't complain about unsed imports
__all__ = ["hive_bp", "track_bp", "users_bp"]
