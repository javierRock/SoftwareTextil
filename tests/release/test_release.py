"""Pruebas acotadas del contrato de empaquetado."""

import hashlib
from pathlib import Path

import pytest

from scripts.package_release import _safe_relative_path, load_config
from scripts.verify_release import (
    REQUIRED_ARCHIVE_FILES,
    _validate_member,
    _validate_required_files,
    _verify_checksum,
)


def test_configuracion_release_usa_metadatos_del_proyecto() -> None:
    config = load_config()

    assert config.name == "software-textil"
    assert config.version == "0.1.0"
    assert config.archive.name == "software-textil-0.1.0.zip"


@pytest.mark.parametrize("path", ["../secret", "/secret", "apps/../../secret"])
def test_configuracion_release_rechaza_rutas_inseguras(path: str) -> None:
    with pytest.raises(ValueError, match="Ruta no permitida"):
        _safe_relative_path(path)


@pytest.mark.parametrize("member", [".env", ".git/config", "media/avatar.png"])
def test_verificacion_rechaza_archivos_excluidos(member: str) -> None:
    with pytest.raises(ValueError, match="excluida"):
        _validate_member(member)


def test_checksum_detecta_un_artefacto_modificado(tmp_path: Path) -> None:
    archive = tmp_path / "release.zip"
    checksum = tmp_path / "release.zip.sha256"
    archive.write_bytes(b"contenido original")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")

    _verify_checksum(archive, checksum)
    archive.write_bytes(b"contenido modificado")

    with pytest.raises(ValueError, match="no coincide"):
        _verify_checksum(archive, checksum)


@pytest.mark.parametrize(
    "asset",
    [
        "frontend/inventario/dist/assets/app.js",
        "frontend/inventario/dist/assets/app.css",
        "build/staticfiles/zuren/assets/app.js",
        "build/staticfiles/zuren/assets/app.css",
    ],
)
def test_verificacion_rechaza_recurso_frontend_faltante(asset: str) -> None:
    with pytest.raises(ValueError, match="Faltan entradas obligatorias"):
        _validate_required_files(REQUIRED_ARCHIVE_FILES - {asset})
