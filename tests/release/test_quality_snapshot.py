import io
import json
import runpy
import sys
from urllib.parse import parse_qs, urlsplit

import pytest


def test_exporta_el_gate_y_todas_las_paginas_de_issues(monkeypatch, tmp_path):
    destination = tmp_path / "exportacion"
    project = "softwaretextil-prueba"
    monkeypatch.setattr(
        sys, "argv", ["quality_snapshot", str(destination), "--project", project]
    )
    monkeypatch.setenv("SONAR_HOST_URL", "http://127.0.0.1:9008")
    monkeypatch.setenv("SONAR_USER", "usuario-prueba")
    monkeypatch.setenv("SONAR_PASSWORD", "clave-prueba")
    gate = {"projectStatus": {"status": "ERROR"}}
    endpoint_responses = {
        "/api/system/status": ({}, {"status": "UP"}),
        "/api/project_analyses/search": ({"project": [project]}, {"analyses": []}),
        "/api/qualitygates/project_status": ({"projectKey": [project]}, gate),
    }
    issue_pages = []

    def respond(request, *, timeout):
        url = urlsplit(request.full_url)
        params = parse_qs(url.query)
        assert url.netloc == "127.0.0.1:9008"
        assert request.get_header("Authorization", "").startswith("Basic ")
        assert timeout == 30
        if url.path == "/api/measures/component":
            assert params["component"] == [project]
            assert "coverage" in params["metricKeys"][0].split(",")
            payload = {"component": {"measures": []}}
        elif url.path == "/api/issues/search":
            page = params["p"][0]
            assert params["componentKeys"] == [project]
            issue_pages.append(page)
            payload = {"total": 2, "issues": [{"key": f"issue-{page}"}]}
        else:
            expected_params, payload = endpoint_responses[url.path]
            assert params == expected_params
        return io.BytesIO(json.dumps(payload).encode())

    monkeypatch.setattr("urllib.request.urlopen", respond)

    runpy.run_module("scripts.quality_snapshot", run_name="__main__")

    assert issue_pages == ["1", "2"]
    expected_exports = {
        "estado.json": {"status": "UP"},
        "analisis.json": {"analyses": []},
        "quality-gate.json": gate,
        "metricas.json": {"component": {"measures": []}},
        "issues.json": {
            "total": 2,
            "issues": [{"key": "issue-1"}, {"key": "issue-2"}],
        },
    }
    assert {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in destination.iterdir()
    } == expected_exports


def test_rechaza_un_servidor_remoto_antes_de_exportar(monkeypatch, tmp_path):
    destination = tmp_path / "exportacion"
    monkeypatch.setattr(sys, "argv", ["quality_snapshot", str(destination)])
    monkeypatch.setenv("SONAR_HOST_URL", "https://sonar.example.invalid")

    with pytest.raises(ValueError, match="limitada al servidor local"):
        runpy.run_module("scripts.quality_snapshot", run_name="__main__")

    assert not destination.exists()
