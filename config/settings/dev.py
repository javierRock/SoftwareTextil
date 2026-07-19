"""Settings de desarrollo. Usa SQLite como fallback temporal hasta tener PostgreSQL."""

from config.settings.base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# TODO: cambiar a PostgreSQL cuando este disponible
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}
