"""Settings aislados para checks y recolección de archivos estáticos."""

from config.settings.base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
STATIC_ROOT = BASE_DIR / "build" / "staticfiles"  # noqa: F405
