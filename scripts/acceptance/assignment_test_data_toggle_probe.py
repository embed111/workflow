#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe assignment test-data bootstrap and global visibility toggle.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8130)
    parser.add_argument("--root", default=".")
    parser.add_argument("--artifacts-dir", default=os.getenv("TEST_ARTIFACTS_DIR") or ".test-artifacts")
    parser.add_argument("--logs-dir", default=os.getenv("TEST_LOG_DIR") or ".test-logs")
    return parser.parse_args()


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json_response(response: urllib.request.addinfourl) -> dict[str, Any]:
    raw = response.read()
    if not raw:
        return {}
    payload = json.loads(raw.decode("utf-8"))
    return payload if isinstance(payload, dict) else {}


def api_request(
    base_url: str,
    method: str,
    route: str,
    body: dict[str, Any] | None = None,
) -> tuple[int, Any]:
    payload = None
    headers = {"Accept": "application/json"}
    if body is not None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        base_url + route,
        data=payload,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            content_type = str(response.headers.get("Content-Type") or "")
            if "application/json" in content_type:
                return int(response.status), read_json_response(response)
            return int(response.status), response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        content_type = str(exc.headers.get("Content-Type") or "")
        if "application/json" in content_type:
            return int(exc.code), read_json_response(exc)
        return int(exc.code), exc.read().decode("utf-8")


def wait_for_health(base_url: str, timeout_s: float = 30.0) -> dict[str, Any]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            status, data = api_request(base_url, "GET", "/healthz")
            if status == 200 and isinstance(data, dict) and data.get("ok"):
                return data
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError("healthz timeout")


def load_workspace_runtime_config(workspace_root: Path) -> dict[str, Any]:
    config_path = workspace_root / ".runtime" / "state" / "runtime-config.json"
    if not config_path.exists():
        return {}
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def prepare_isolated_runtime_root(workspace_root: Path, artifacts_dir: Path) -> tuple[Path, dict[str, Any]]:
    runtime_root = (Path(os.getenv("TEST_TMP_DIR") or artifacts_dir) / "workflow-runtime-assignment-test-data").resolve()
    state_dir = runtime_root / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    source_cfg = load_workspace_runtime_config(workspace_root)
    bootstrap_cfg: dict[str, Any] = {"show_test_data": False}
    agent_search_root = str(source_cfg.get("agent_search_root") or "").strip()
    if agent_search_root:
        bootstrap_cfg["agent_search_root"] = agent_search_root
    (state_dir / "runtime-config.json").write_text(
        json.dumps(bootstrap_cfg, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return runtime_root, bootstrap_cfg


def fetch_db_graph_row(db_path: Path, ticket_id: str) -> dict[str, Any]:
    conn = sqlite3.connect(db_path.as_posix())
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """
            SELECT ticket_id,graph_name,source_workflow,external_request_id,is_test_data,scheduler_state,updated_at
            FROM assignment_graphs
            WHERE ticket_id=?
            LIMIT 1
            """,
            (ticket_id,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return {}
    return {name: row[name] for name in row.keys()}


def main() -> int:
    args = parse_args()
    workspace_root = Path(args.root).resolve()
    artifacts_dir = Path(args.artifacts_dir).resolve()
    logs_dir = Path(args.logs_dir).resolve()
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = artifacts_dir / "assignment-test-data-toggle-probe.json"
    server_stdout = logs_dir / "assignment-test-data-toggle-server.stdout.log"
    server_stderr = logs_dir / "assignment-test-data-toggle-server.stderr.log"
    runtime_root, bootstrap_cfg = prepare_isolated_runtime_root(workspace_root, artifacts_dir)
    runtime_db = runtime_root / "state" / "workflow.db"
    base_url = f"http://{args.host}:{args.port}"
    stdout_handle = server_stdout.open("ab")
    stderr_handle = server_stderr.open("ab")
    server = subprocess.Popen(
        [
            sys.executable,
            "scripts/workflow_web_server.py",
            "--root",
            str(runtime_root),
            "--host",
            args.host,
            "--port",
            str(args.port),
        ],
        cwd=str(workspace_root),
        stdout=stdout_handle,
        stderr=stderr_handle,
    )

    evidence: dict[str, Any] = {
        "workspace_root": str(workspace_root),
        "runtime_root": str(runtime_root),
        "runtime_db": str(runtime_db),
        "runtime_bootstrap_config": bootstrap_cfg,
        "base_url": base_url,
    }

    try:
        evidence["healthz"] = wait_for_health(base_url)

        status, agents_payload = api_request(base_url, "GET", "/api/agents")
        assert_true(status == 200 and isinstance(agents_payload, dict) and agents_payload.get("ok"), "agents api unavailable")
        artifact_root = Path(str(agents_payload.get("artifact_root") or "").strip()).resolve()
        assert_true(artifact_root.name.lower() == ".output", "artifact_root should resolve to ../.output")
        evidence["artifact_root"] = str(artifact_root)
        evidence["artifact_workspace_root"] = str(Path(str(agents_payload.get("artifact_workspace_root") or "")).resolve())

        status, hidden_cfg = api_request(base_url, "GET", "/api/config/show-test-data")
        assert_true(status == 200 and isinstance(hidden_cfg, dict) and hidden_cfg.get("ok"), "show-test-data config unavailable")
        assert_true(hidden_cfg.get("show_test_data") is False, "show_test_data should start as false")
        evidence["initial_show_test_data"] = hidden_cfg

        status, hidden_bootstrap = api_request(
            base_url,
            "POST",
            "/api/assignments/test-data/bootstrap",
            {"operator": "assignment-test-data-toggle-probe"},
        )
        assert_true(status == 409, "bootstrap should be rejected when show_test_data=false")
        assert_true(
            isinstance(hidden_bootstrap, dict)
            and str(hidden_bootstrap.get("code") or "").strip() == "assignment_test_data_hidden",
            "unexpected hidden bootstrap error code",
        )
        evidence["hidden_bootstrap"] = hidden_bootstrap

        status, hidden_list = api_request(base_url, "GET", "/api/assignments")
        assert_true(status == 200 and isinstance(hidden_list, dict) and hidden_list.get("ok"), "hidden assignment list unavailable")
        hidden_items = list(hidden_list.get("items") or [])
        assert_true(not hidden_items, "isolated runtime should not expose assignment graphs while hidden")
        evidence["hidden_list"] = hidden_list

        status, show_on = api_request(
            base_url,
            "POST",
            "/api/config/show-test-data",
            {"show_test_data": True},
        )
        assert_true(status == 200 and isinstance(show_on, dict) and show_on.get("ok"), "enable show_test_data failed")
        assert_true(show_on.get("show_test_data") is True, "show_test_data should be true after enable")
        evidence["show_on"] = show_on

        status, bootstrap = api_request(
            base_url,
            "POST",
            "/api/assignments/test-data/bootstrap",
            {"operator": "assignment-test-data-toggle-probe"},
        )
        assert_true(status == 200 and isinstance(bootstrap, dict) and bootstrap.get("ok"), "bootstrap assignment test data failed")
        ticket_id = str(bootstrap.get("ticket_id") or "").strip()
        assert_true(ticket_id, "bootstrap ticket_id missing")
        evidence["bootstrap"] = bootstrap

        status, visible_list = api_request(base_url, "GET", "/api/assignments?include_test_data=1")
        assert_true(status == 200 and isinstance(visible_list, dict) and visible_list.get("ok"), "visible assignment list unavailable")
        visible_items = list(visible_list.get("items") or [])
        visible_graph = next(
            (
                item
                for item in visible_items
                if str((item or {}).get("ticket_id") or "").strip() == ticket_id
            ),
            {},
        )
        assert_true(bool(visible_graph), "bootstrapped test graph missing from visible list")
        assert_true(bool(visible_graph.get("is_test_data")), "bootstrapped graph must be marked as test data")
        evidence["visible_list"] = visible_list

        status, graph_payload = api_request(
            base_url,
            "GET",
            f"/api/assignments/{ticket_id}/graph?history_loaded=24&history_batch_size=24&include_test_data=1",
        )
        assert_true(status == 200 and isinstance(graph_payload, dict) and graph_payload.get("ok"), "graph fetch after bootstrap failed")
        graph = graph_payload.get("graph") or {}
        counts = ((graph_payload.get("metrics_summary") or {}).get("status_counts") or {})
        nodes = list(graph_payload.get("nodes") or [])
        node_map = {
            str((item or {}).get("node_id") or "").strip(): item
            for item in nodes
            if str((item or {}).get("node_id") or "").strip()
        }
        assert_true(bool(graph.get("is_test_data")), "graph payload should expose is_test_data=true")
        assert_true(int((graph_payload.get("metrics_summary") or {}).get("total_nodes") or 0) == 20, "prototype graph should seed 20 nodes")
        assert_true(int(counts.get("succeeded") or 0) >= 1, "prototype graph should include succeeded nodes")
        assert_true(int(counts.get("running") or 0) == 1, "prototype graph should include one running node")
        assert_true(int(counts.get("failed") or 0) == 1, "prototype graph should include one failed node")
        assert_true(int(counts.get("blocked") or 0) >= 1, "prototype graph should include blocked nodes")
        assert_true("T17" in node_map, "independent node T17 missing")
        assert_true(not list((node_map.get("T17") or {}).get("upstream_node_ids") or []), "T17 should stay independent")
        evidence["graph_payload"] = {
            "ticket_id": ticket_id,
            "graph": graph,
            "metrics_summary": graph_payload.get("metrics_summary"),
            "node_ids": sorted(node_map.keys()),
        }

        status, preview_payload = api_request(
            base_url,
            "GET",
            f"/api/assignments/{ticket_id}/nodes/T8/artifact-preview?include_test_data=1",
        )
        assert_true(status == 200 and isinstance(preview_payload, str), "artifact preview for seeded node T8 failed")
        assert_true("依赖关系图" in preview_payload, "artifact preview content mismatch")
        evidence["artifact_preview_excerpt"] = preview_payload[:240]

        db_graph_row = fetch_db_graph_row(runtime_db, ticket_id)
        assert_true(bool(db_graph_row), "bootstrapped graph missing from runtime db")
        assert_true(int(db_graph_row.get("is_test_data") or 0) == 1, "runtime db graph should mark is_test_data=1")
        evidence["db_graph_row"] = db_graph_row

        workspace_graph_path = artifact_root / "workspace" / "assignments" / ticket_id / "graph.json"
        assert_true(workspace_graph_path.exists(), "workspace graph snapshot missing")
        workspace_graph_payload = json.loads(workspace_graph_path.read_text(encoding="utf-8"))
        assert_true(bool(workspace_graph_payload.get("is_test_data")), "workspace graph snapshot should preserve is_test_data")
        evidence["workspace_graph_path"] = str(workspace_graph_path)
        evidence["workspace_graph_snapshot"] = workspace_graph_payload

        status, show_off = api_request(
            base_url,
            "POST",
            "/api/config/show-test-data",
            {"show_test_data": False},
        )
        assert_true(status == 200 and isinstance(show_off, dict) and show_off.get("ok"), "disable show_test_data failed")
        assert_true(show_off.get("show_test_data") is False, "show_test_data should be false after disable")
        evidence["show_off"] = show_off

        status, hidden_again = api_request(base_url, "GET", "/api/assignments")
        assert_true(status == 200 and isinstance(hidden_again, dict) and hidden_again.get("ok"), "assignment list unavailable after hide")
        hidden_again_items = list(hidden_again.get("items") or [])
        assert_true(
            all(str((item or {}).get("ticket_id") or "").strip() != ticket_id for item in hidden_again_items),
            "test graph should disappear after show_test_data=false",
        )
        evidence["hidden_again"] = hidden_again

        status, hidden_graph = api_request(
            base_url,
            "GET",
            f"/api/assignments/{ticket_id}/graph?history_loaded=24&history_batch_size=24&include_test_data=0",
        )
        assert_true(status == 404, "hidden test graph should return 404")
        assert_true(
            isinstance(hidden_graph, dict)
            and str(hidden_graph.get("code") or "").strip() == "assignment_graph_not_found",
            "unexpected hidden graph error code",
        )
        evidence["hidden_graph_fetch"] = hidden_graph

        status, hidden_preview = api_request(
            base_url,
            "GET",
            f"/api/assignments/{ticket_id}/nodes/T8/artifact-preview?include_test_data=0",
        )
        assert_true(status == 404, "hidden test artifact preview should return 404")
        evidence["hidden_artifact_preview"] = hidden_preview

        evidence["ok"] = True
        evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=10)
        stdout_handle.close()
        stderr_handle.close()
        if not evidence_path.exists():
            evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
