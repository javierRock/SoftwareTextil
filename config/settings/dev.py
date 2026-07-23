"""Settings de desarrollo. Usa SQLite como fallback temporal hasta tener PostgreSQL."""

from config.settings.base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# SQLite queda como respaldo temporal para desarrollo local hasta disponer de PostgreSQL.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}
