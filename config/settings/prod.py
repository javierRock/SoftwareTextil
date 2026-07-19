"""Settings de produccion con PostgreSQL."""

import os

from config.settings.base import *  # noqa: F401, F403

DEBUG = False
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
