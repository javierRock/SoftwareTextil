"""Empaqueta las fuentes versionadas y la SPA; funciona tambien desde el ZIP."""

# Git resuelto desde PATH, argumentos constantes y sin shell.
# ruff: noqa: S603

import hashlib
import json
import shutil
import subprocess
import tomllib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]


def main():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    prefix = f"{project['name']}-{project['version']}"
    frontend = ROOT / "frontend/inventario/dist"
    if not (frontend / "index.html").is_file():
        raise SystemExit("Falta la SPA compilada. Ejecute make build primero.")

    # .git debe pertenecer a esta copia, no al directorio padre del usuario.
    if (ROOT / ".git").exists():
        git = shutil.which("git")
        if git is None:
            raise SystemExit("Git no esta disponible en PATH.")
        tracked = (
            subprocess.check_output([git, "ls-files", "-z"], cwd=ROOT)
            .decode()
            .split("\0")
        )
        sources = sorted(name for name in tracked if name)
        revision = subprocess.check_output(
            [git, "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        dirty = bool(subprocess.check_output([git, "status", "--porcelain"], cwd=ROOT))
    else:
        manifest = ROOT / "BUILD-MANIFEST.json"
        if not manifest.exists():
            raise SystemExit(
                "Se requiere un clon Git o el ZIP con BUILD-MANIFEST.json."
            )
        previous = json.loads(manifest.read_text())
        sources = previous["source_files"]
        revision = previous["git_revision"]
        dirty = True  # Una copia extraida no puede certificar un arbol Git limpio.

    # No se admiten secretos ni dependencias instaladas, aunque se versionen por error.
    for name in sources:
        path = Path(name)
        if (
            path.is_absolute()
            or ".." in path.parts
            or any(
                part in {".git", ".venv", "node_modules", "media"}
                or (part.startswith(".env") and part != ".env.example")
                for part in path.parts
            )
        ):
            raise SystemExit(f"Ruta no permitida en el respaldo: {name}")
        if not (ROOT / name).is_file() or (ROOT / name).is_symlink():
            raise SystemExit(f"Fuente ausente o enlace no admitido: {name}")

    files = sorted(
        set(sources)
        | {p.relative_to(ROOT).as_posix() for p in frontend.rglob("*") if p.is_file()}
    )
    manifest = {
        "project": project["name"],
        "version": project["version"],
        "git_revision": revision,
        "working_tree_modified": dirty,
        "source_files": sources,
        "sha256": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in files
        },
        "note": (
            "Fuentes y SPA; no incluye base de datos, secretos "
            "ni dependencias instaladas."
        ),
    }
    destination = ROOT / "dist"
    destination.mkdir(exist_ok=True)
    archive = destination / f"{prefix}.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as output:
        for name in files:
            output.write(ROOT / name, f"{prefix}/{name}")
        output.writestr(
            f"{prefix}/BUILD-MANIFEST.json",
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        )
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".zip.sha256").write_text(f"{checksum}  {archive.name}\n")
    print(f"Paquete: {archive.name} ({len(files)} archivos + manifiesto)")
    print(f"SHA-256: {checksum}")


if __name__ == "__main__":
    main()
