"""Genera una distribución ZIP verificable de SoftwareTextil."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_NAME = "RELEASE-MANIFEST.json"
EXCLUDED_PARTS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "media",
    "node_modules",
}
EXCLUDED_NAMES = {".env", "db.sqlite3"}


@dataclass(frozen=True)
class ReleaseConfig:
    name: str
    version: str
    output_dir: Path
    entries: tuple[Path, ...]

    @property
    def archive(self) -> Path:
        return self.output_dir / f"{self.name}-{self.version}.zip"


def load_config(root: Path = ROOT) -> ReleaseConfig:
    """Parsea y valida la configuración de release en pyproject.toml."""
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    project = data["project"]
    release = data["tool"]["software-textil"]["release"]
    if release.get("format") != "zip":
        raise ValueError("tool.software-textil.release.format debe ser 'zip'")
    entries = tuple(_safe_relative_path(value) for value in release["entries"])
    return ReleaseConfig(
        name=project["name"],
        version=project["version"],
        output_dir=root / _safe_relative_path(release["output-dir"]),
        entries=entries,
    )


def _safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Ruta no permitida en configuración de release: {value}")
    return path


def _included_file(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return not (
        path.name in EXCLUDED_NAMES
        or any(part in EXCLUDED_PARTS for part in relative.parts)
        or path.suffix in {".pyc", ".pyo"}
    )


def collect_files(config: ReleaseConfig) -> list[Path]:
    """Resuelve la lista explícita de entradas y rechaza faltantes."""
    files: list[Path] = []
    for relative in config.entries:
        source = ROOT / relative
        if not source.exists():
            raise FileNotFoundError(f"Falta una entrada obligatoria: {relative}")
        candidates = [source] if source.is_file() else source.rglob("*")
        for path in candidates:
            if path.is_file() and _included_file(path):
                files.append(path)
    unique = {path.relative_to(ROOT).as_posix(): path for path in files}
    return [unique[name] for name in sorted(unique)]


def _validate_frontend() -> None:
    index = ROOT / "frontend" / "inventario" / "dist" / "index.html"
    app_js = ROOT / "frontend" / "inventario" / "dist" / "assets" / "app.js"
    app_css = ROOT / "frontend" / "inventario" / "dist" / "assets" / "app.css"
    collected_js = ROOT / "build" / "staticfiles" / "zuren" / "assets" / "app.js"
    collected_css = ROOT / "build" / "staticfiles" / "zuren" / "assets" / "app.css"
    if not index.is_file() or not app_js.is_file() or not app_css.is_file():
        raise FileNotFoundError(
            "El build frontend no contiene index.html, assets/app.js y assets/app.css"
        )
    index_content = index.read_text(encoding="utf-8")
    referenced_assets = (
        "/static/zuren/assets/app.js",
        "/static/zuren/assets/app.css",
    )
    for asset in referenced_assets:
        if asset not in index_content:
            raise ValueError(f"index.html no referencia {asset}")
    if not collected_js.is_file() or not collected_css.is_file():
        raise FileNotFoundError(
            "collectstatic no produjo zuren/assets/app.js y zuren/assets/app.css"
        )


def _command_output(command: list[str]) -> str:
    try:
        executable = shutil.which(command[0])
        if executable is None:
            return f"no disponible ({command[0]} no está instalado)"
        return subprocess.run(  # noqa: S603 - solo ejecuta herramientas internas conocidas
            [executable, *command[1:]],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        return f"no disponible ({error})"


def _manifest(config: ReleaseConfig, names: list[str]) -> dict[str, object]:
    status = _command_output(["git", "status", "--porcelain", "--untracked-files=all"])
    return {
        "project": config.name,
        "version": config.version,
        "format": "zip",
        "source_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "source_state": "con cambios" if status else "limpio",
        "tools": {
            "python": sys.version.split()[0],
            "uv": _command_output(["uv", "--version"]),
            "node": _command_output(["node", "--version"]),
            "npm": _command_output(["npm", "--version"]),
            "make": _command_output(["make", "--version"]).splitlines()[0],
        },
        "files": names,
    }


def _write_archive(
    destination: Path,
    files: list[Path],
    manifest: dict[str, object],
) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in files:
            archive.write(source, source.relative_to(ROOT).as_posix())
        archive.writestr(
            MANIFEST_NAME,
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )


def build_release() -> tuple[Path, Path]:
    """Construye ZIP y checksum sin dejar artefactos parciales."""
    config = load_config()
    _validate_frontend()
    files = collect_files(config)
    names = [path.relative_to(ROOT).as_posix() for path in files]
    manifest = _manifest(config, names)
    config.output_dir.mkdir(parents=True, exist_ok=True)
    checksum_path = Path(f"{config.archive}.sha256")
    config.archive.unlink(missing_ok=True)
    checksum_path.unlink(missing_ok=True)

    temporary_directory = Path(
        tempfile.mkdtemp(prefix="release-", dir=config.output_dir)
    )
    try:
        temporary_archive = temporary_directory / config.archive.name
        _write_archive(temporary_archive, files, manifest)
        digest = hashlib.sha256(temporary_archive.read_bytes()).hexdigest()
        temporary_checksum = temporary_directory / checksum_path.name
        temporary_checksum.write_text(
            f"{digest}  {config.archive.name}\n",
            encoding="utf-8",
        )
        os.replace(temporary_archive, config.archive)
        os.replace(temporary_checksum, checksum_path)
    finally:
        shutil.rmtree(temporary_directory, ignore_errors=True)

    return config.archive, checksum_path


def main() -> None:
    try:
        archive, checksum = build_release()
    except (KeyError, OSError, ValueError, zipfile.BadZipFile) as error:
        raise SystemExit(f"Error al empaquetar: {error}") from error
    print(f"ZIP: {archive.relative_to(ROOT)}")
    print(f"SHA-256: {checksum.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
