#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe assignment artifact root and delivery flow.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8129)
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


def api_request(base_url: str, method: str, route: str, body: dict[str, Any] | None = None) -> tuple[int, Any]:
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
        with urllib.request.urlopen(request, timeout=15) as response:
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
    runtime_root = (Path(os.getenv("TEST_TMP_DIR") or artifacts_dir) / "workflow-runtime").resolve()
    state_dir = runtime_root / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    source_cfg = load_workspace_runtime_config(workspace_root)
    bootstrap_cfg: dict[str, Any] = {}
    agent_search_root = str(source_cfg.get("agent_search_root") or "").strip()
    if agent_search_root:
        bootstrap_cfg["agent_search_root"] = agent_search_root
    if "show_test_data" in source_cfg:
        bootstrap_cfg["show_test_data"] = bool(source_cfg.get("show_test_data"))
    if bootstrap_cfg:
        (state_dir / "runtime-config.json").write_text(
            json.dumps(bootstrap_cfg, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return runtime_root, bootstrap_cfg


def main() -> int:
    args = parse_args()
    workspace_root = Path(args.root).resolve()
    artifacts_dir = Path(args.artifacts_dir).resolve()
    logs_dir = Path(args.logs_dir).resolve()
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = artifacts_dir / "assignment-artifact-root-probe.json"
    server_stdout = logs_dir / "assignment-artifact-root-server.stdout.log"
    server_stderr = logs_dir / "assignment-artifact-root-server.stderr.log"
    base_url = f"http://{args.host}:{args.port}"
    runtime_root, bootstrap_cfg = prepare_isolated_runtime_root(workspace_root, artifacts_dir)

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
        "runtime_bootstrap_config": bootstrap_cfg,
        "base_url": base_url,
    }

    try:
        evidence["healthz"] = wait_for_health(base_url)

        status, agents_payload = api_request(base_url, "GET", "/api/agents")
        assert_true(status == 200 and isinstance(agents_payload, dict) and agents_payload.get("ok"), "agents api unavailable")
        artifact_root = Path(str(agents_payload.get("artifact_root") or "").strip()).resolve()
        workspace_record_root = Path(str(agents_payload.get("artifact_workspace_root") or "").strip()).resolve()
        assert_true(workspace_record_root == artifact_root / "workspace", "workspace root must be under artifact root")
        assert_true(artifact_root.name.lower() == ".output", "default artifact root should resolve to ../.output")
        evidence["artifact_root"] = str(artifact_root)
        evidence["workspace_record_root"] = str(workspace_record_root)

        status, training_agents = api_request(base_url, "GET", "/api/training/agents")
        assert_true(status == 200 and isinstance(training_agents, dict) and training_agents.get("ok"), "training agents unavailable")
        agent_rows = list(training_agents.get("items") or [])
        agent_ids = [
            str((item or {}).get("agent_id") or "").strip()
            for item in agent_rows
            if str((item or {}).get("agent_id") or "").strip()
        ]
        assert_true(bool(agent_ids), "no training agents available")
        worker_agent_id = agent_ids[0]
        receiver_agent_id = agent_ids[1] if len(agent_ids) > 1 else agent_ids[0]

        status, create_graph = api_request(
            base_url,
            "POST",
            "/api/assignments",
            {
                "graph_name": "产物路径探针",
                "source_workflow": "assignment-artifact-root-probe",
                "summary": "probe artifact root and delivery flow",
                "review_mode": "none",
                "external_request_id": f"artifact-root-{int(time.time() * 1000)}",
                "operator": "assignment-artifact-root-probe",
            },
        )
        assert_true(status == 200 and isinstance(create_graph, dict) and create_graph.get("ok"), "create graph failed")
        ticket_id = str(create_graph.get("ticket_id") or "").strip()
        assert_true(ticket_id, "ticket id missing")
        evidence["ticket_id"] = ticket_id

        status, create_node = api_request(
            base_url,
            "POST",
            f"/api/assignments/{ticket_id}/nodes",
            {
                "node_name": "统一产物交付验证",
                "assigned_agent_id": worker_agent_id,
                "priority": "P0",
                "node_goal": "验证产物根路径与交付门禁",
                "expected_artifact": "验证报告",
                "delivery_mode": "specified",
                "delivery_receiver_agent_id": receiver_agent_id,
                "operator": "assignment-artifact-root-probe",
            },
        )
        assert_true(status == 200 and isinstance(create_node, dict) and create_node.get("ok"), "create node failed")
        node_id = str(((create_node.get("node") or {}).get("node_id")) or "").strip()
        assert_true(node_id, "node id missing")
        evidence["node_id"] = node_id

        status, _resume = api_request(
            base_url,
            "POST",
            f"/api/assignments/{ticket_id}/resume",
            {"operator": "assignment-artifact-root-probe"},
        )
        assert_true(status == 200, "resume scheduler failed")
        status, dispatch_payload = api_request(
            base_url,
            "POST",
            f"/api/assignments/{ticket_id}/dispatch-next",
            {"operator": "assignment-artifact-root-probe"},
        )
        assert_true(status == 200 and isinstance(dispatch_payload, dict) and dispatch_payload.get("ok"), "dispatch failed")

        blocked_status, blocked_payload = api_request(
            base_url,
            "POST",
            f"/api/assignments/{ticket_id}/nodes/{node_id}/mark-success",
            {
                "success_reason": "未交付前尝试成功",
                "result_ref": "probe://before-delivery",
                "operator": "assignment-artifact-root-probe",
            },
        )
        assert_true(blocked_status == 409, "mark success should be blocked before delivery")
        assert_true(
            isinstance(blocked_payload, dict) and str(blocked_payload.get("code") or "").strip() == "artifact_delivery_required",
            "unexpected block code before delivery",
        )

        status, deliver_payload = api_request(
            base_url,
            "POST",
            f"/api/assignments/{ticket_id}/nodes/{node_id}/deliver-artifact",
            {
                "artifact_label": "验证报告",
                "delivery_note": "统一产物交付探针写入",
                "operator": "assignment-artifact-root-probe",
            },
        )
        assert_true(status == 200 and isinstance(deliver_payload, dict) and deliver_payload.get("ok"), "deliver artifact failed")
        delivered_paths = [str(item).strip() for item in list(deliver_payload.get("artifact_paths") or []) if str(item).strip()]
        assert_true(len(delivered_paths) == 2, "specified delivery should create product and receive paths")
        for item in delivered_paths:
            path = Path(item).resolve()
            assert_true(path.exists(), f"artifact file missing: {path}")
            assert_true(str(path).startswith(str(artifact_root)), f"artifact path out of root: {path}")

        status, mark_success = api_request(
            base_url,
            "POST",
            f"/api/assignments/{ticket_id}/nodes/{node_id}/mark-success",
            {
                "success_reason": "产物交付后允许成功",
                "result_ref": "probe://after-delivery",
                "operator": "assignment-artifact-root-probe",
            },
        )
        assert_true(status == 200 and isinstance(mark_success, dict) and mark_success.get("ok"), "mark success after delivery failed")

        status, detail_payload = api_request(
            base_url,
            "GET",
            f"/api/assignments/{ticket_id}/status-detail?node_id={node_id}",
        )
        assert_true(status == 200 and isinstance(detail_payload, dict) and detail_payload.get("ok"), "status detail fetch failed")
        selected_node = detail_payload.get("selected_node") or {}
        assert_true(str(selected_node.get("artifact_delivery_status") or "").strip() == "delivered", "artifact delivery status mismatch")
        assert_true(len(list(selected_node.get("artifact_paths") or [])) == 2, "status detail artifact paths mismatch")

        preview_status, preview_text = api_request(
            base_url,
            "GET",
            f"/api/assignments/{ticket_id}/nodes/{node_id}/artifact-preview",
        )
        assert_true(preview_status == 200, "artifact preview should be readable")
        assert_true("统一产物交付探针写入" in str(preview_text), "artifact preview content mismatch")

        workspace_ticket_dir = workspace_record_root / "assignments" / ticket_id
        workspace_graph = workspace_ticket_dir / "graph.json"
        workspace_node = workspace_ticket_dir / "nodes" / f"{node_id}.json"
        assert_true(workspace_graph.exists(), "workspace graph record missing")
        assert_true(workspace_node.exists(), "workspace node record missing")

        evidence["delivery_gate"] = {
            "blocked_before_delivery": blocked_payload,
            "deliver_response": deliver_payload,
            "mark_success_response": mark_success,
        }
        evidence["artifact_paths"] = delivered_paths
        evidence["artifact_preview"] = str(preview_text)
        evidence["workspace_records"] = {
            "ticket_dir": str(workspace_ticket_dir),
            "graph_record": str(workspace_graph),
            "node_record": str(workspace_node),
        }
        evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"evidence_path": str(evidence_path), "ticket_id": ticket_id, "node_id": node_id}, ensure_ascii=False, indent=2))
        return 0
    finally:
        try:
            server.terminate()
            server.wait(timeout=5)
        except Exception:
            try:
                server.kill()
            except Exception:
                pass
        stdout_handle.close()
        stderr_handle.close()


if __name__ == "__main__":
    raise SystemExit(main())
