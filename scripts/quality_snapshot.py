"""Exporta un análisis local SonarQube ya completado, sin alterar sus issues."""

import argparse
import base64
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destino", type=Path)
    parser.add_argument("--project", default="softwaretextil-quality-review")
    args = parser.parse_args()
    host = os.environ.get("SONAR_HOST_URL", "http://127.0.0.1:9008")
    if host not in {"http://127.0.0.1:9007", "http://127.0.0.1:9008"}:
        raise ValueError("Esta herramienta está limitada al servidor local")
    user = os.environ.get("SONAR_USER", "admin")
    password = os.environ.get("SONAR_PASSWORD", "admin")
    auth = base64.b64encode(f"{user}:{password}".encode()).decode()
    key = args.project

    def get(endpoint, **params):
        request = Request(  # noqa: S310 - host local exacto validado arriba
            f"{host}/api/{endpoint}?{urlencode(params)}",
            headers={"Authorization": f"Basic {auth}"},
        )
        with urlopen(request, timeout=30) as response:  # noqa: S310
            return json.load(response)

    args.destino.mkdir(parents=True, exist_ok=True)

    def save(name, value):
        (args.destino / name).write_text(
            json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    save("estado.json", get("system/status"))
    save("analisis.json", get("project_analyses/search", project=key))
    save("quality-gate.json", get("qualitygates/project_status", projectKey=key))
    save("metricas.json", get(
        "measures/component", component=key,
        metricKeys="bugs,vulnerabilities,code_smells,sqale_index,coverage,duplicated_lines_density,ncloc,security_hotspots",
    ))
    issues = []
    page = 1
    while True:
        batch = get("issues/search", componentKeys=key, ps=500, p=page)
        issues.extend(batch["issues"])
        if len(issues) >= batch["total"]:
            break
        page += 1
    save("issues.json", {"total": len(issues), "issues": issues})
    print(f"Exportados {len(issues)} issues a {args.destino}")


if __name__ == "__main__":
    main()
