"""Settings de desarrollo. Usa el mismo PostgreSQL que produccion.

Compartir motor con produccion es lo que permite que las restricciones del
esquema (CHECK, indices parciales y unicidad sobre `Lower(...)`) se validen en
las pruebas y no recien al desplegar. El contenedor se levanta con
`docker compose up -d`.
"""

from config.settings.base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
