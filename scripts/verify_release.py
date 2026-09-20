"""Verifica el contrato del ZIP desde una extracción fuera del repositorio."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from scripts.package_release import (
    EXCLUDED_NAMES,
    EXCLUDED_PARTS,
    MANIFEST_NAME,
    load_config,
)

REQUIRED_ARCHIVE_FILES = {
    MANIFEST_NAME,
    "manage.py",
    "pyproject.toml",
    "uv.lock",
    "frontend/inventario/dist/index.html",
    "frontend/inventario/dist/assets/app.js",
    "frontend/inventario/dist/assets/app.css",
    "build/staticfiles/zuren/assets/app.js",
    "build/staticfiles/zuren/assets/app.css",
}


def _validate_member(name: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Ruta insegura en el ZIP: {name}")
    excluded_part = any(part in EXCLUDED_PARTS for part in path.parts)
    if path.name in EXCLUDED_NAMES or excluded_part:
        raise ValueError(f"Entrada excluida presente en el ZIP: {name}")


def _verify_checksum(archive: Path, checksum_path: Path) -> None:
    expected, filename = (
        checksum_path.read_text(encoding="utf-8").strip().split(maxsplit=1)
    )
    if filename.strip() != archive.name:
        raise ValueError("El checksum referencia un archivo diferente")
    actual = hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError("El checksum SHA-256 no coincide")


def _validate_required_files(names: set[str]) -> None:
    missing = REQUIRED_ARCHIVE_FILES - names
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Faltan entradas obligatorias: {missing_list}")


def verify_release() -> Path:
    config = load_config()
    archive = config.archive
    checksum_path = Path(f"{archive}.sha256")
    if not archive.is_file() or not checksum_path.is_file():
        raise FileNotFoundError("No se encontraron el ZIP y su checksum")
    _verify_checksum(archive, checksum_path)

    extraction_root = Path(tempfile.mkdtemp(prefix="software-textil-release-"))
    with zipfile.ZipFile(archive) as package:
        names = set(package.namelist())
        for name in names:
            _validate_member(name)
        _validate_required_files(names)
        manifest = json.loads(package.read(MANIFEST_NAME))
        if set(manifest["files"]) != names - {MANIFEST_NAME}:
            raise ValueError("El inventario del manifiesto no coincide con el ZIP")
        package.extractall(extraction_root)

    index = extraction_root / "frontend" / "inventario" / "dist" / "index.html"
    index_content = index.read_text(encoding="utf-8")
    for asset in ("app.js", "app.css"):
        if f"/static/zuren/assets/{asset}" not in index_content:
            raise ValueError(f"La SPA extraída no referencia {asset}")

    uv = shutil.which("uv")
    if uv is None:
        raise FileNotFoundError("uv no está instalado")
    subprocess.run(  # noqa: S603 - uv se resuelve desde PATH sin shell
        [uv, "sync", "--locked", "--no-dev"],
        cwd=extraction_root,
        check=True,
    )
    subprocess.run(  # noqa: S603 - uv se resuelve desde PATH sin shell
        [
            uv,
            "run",
            "--locked",
            "--no-dev",
            "python",
            "manage.py",
            "check",
            "--settings=config.settings.build",
        ],
        cwd=extraction_root,
        check=True,
    )
    return extraction_root


def main() -> None:
    try:
        extraction_root = verify_release()
    except (
        KeyError,
        OSError,
        ValueError,
        zipfile.BadZipFile,
        subprocess.CalledProcessError,
    ) as error:
        raise SystemExit(f"Error al verificar el release: {error}") from error
    print(f"Release verificado fuera del repositorio: {extraction_root}")


if __name__ == "__main__":
    main()
