"""Adaptadores de seguridad de infraestructura."""

from werkzeug.security import check_password_hash, generate_password_hash


class WorkzeugPasswordHasher:
    nombre = "werkzeug-pbkdf2"

    def hash(self, password: str) -> str:
        return generate_password_hash(password)

    def verify(self, password: str, password_hash: str, salt: str = "") -> bool:
        return check_password_hash(password_hash, password)
