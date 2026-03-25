#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlencode


IMAGE_DATA_URL = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+cC8QAAAAASUVORK5CYII="
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Browser acceptance for defect center.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8148)
    parser.add_argument(
        "--artifacts-dir",
        default=os.getenv("TEST_ARTIFACTS_DIR") or ".test/evidence",
    )
    parser.add_argument(
        "--logs-dir",
        default=os.getenv("TEST_LOG_DIR") or ".test/evidence",
    )
    return parser.parse_args()


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    *,
    timeout_s: int = 30,
) -> tuple[int, Any]:
    payload = None
    headers = {"Accept": "application/json"}
    if body is not None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(base_url + route, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=max(5, int(timeout_s))) as response:
            content_type = str(response.headers.get("Content-Type") or "")
            if "application/json" in content_type:
                return int(response.status), read_json_response(response)
            return int(response.status), response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        content_type = str(exc.headers.get("Content-Type") or "")
        if "application/json" in content_type:
            return int(exc.code), read_json_response(exc)
        return int(exc.code), exc.read().decode("utf-8")


def wait_for_health(base_url: str, timeout_s: float = 45.0) -> dict[str, Any]:
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
    for candidate in (
        workspace_root / ".runtime" / "state" / "runtime-config.json",
        workspace_root / "state" / "runtime-config.json",
    ):
        if not candidate.exists():
            continue
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return payload if isinstance(payload, dict) else {}
    return {}


def looks_like_workspace_root(path: str) -> bool:
    text = str(path or "").strip()
    if not text:
        return False
    candidate = Path(text).resolve()
    return candidate.exists() and candidate.is_dir() and (candidate / "workflow").exists()


def infer_agent_search_root(workspace_root: Path) -> str:
    base = workspace_root.resolve()
    for candidate in [base, *base.parents]:
        if looks_like_workspace_root(candidate.as_posix()):
            return candidate.as_posix()
    return workspace_root.parent.as_posix()


def prepare_isolated_runtime_root(workspace_root: Path, runtime_root: Path) -> tuple[Path, dict[str, Any]]:
    runtime_root = runtime_root.resolve()
    state_dir = runtime_root / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    source_cfg = load_workspace_runtime_config(workspace_root)
    bootstrap_cfg: dict[str, Any] = {"show_test_data": True}
    configured_agent_root = str(source_cfg.get("agent_search_root") or "").strip()
    fallback_agent_root = infer_agent_search_root(workspace_root)
    agent_search_root = configured_agent_root if looks_like_workspace_root(configured_agent_root) else fallback_agent_root
    artifact_root = str(source_cfg.get("artifact_root") or source_cfg.get("task_artifact_root") or "").strip()
    if agent_search_root:
        bootstrap_cfg["agent_search_root"] = agent_search_root
    if artifact_root:
        bootstrap_cfg["artifact_root"] = artifact_root
        bootstrap_cfg["task_artifact_root"] = artifact_root
    (state_dir / "runtime-config.json").write_text(
        json.dumps(bootstrap_cfg, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return runtime_root, bootstrap_cfg


def find_edge() -> Path:
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for path in candidates:
        if path.exists() and path.is_file():
            return path
    raise RuntimeError("msedge not found")


def edge_cmd(edge_path: Path, profile_dir: Path, width: int, height: int, budget_ms: int) -> list[str]:
    profile_dir.mkdir(parents=True, exist_ok=True)
    return [
        str(edge_path),
        "--headless=new",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-sync",
        "--disable-default-apps",
        "--disable-popup-blocking",
        "--disable-crash-reporter",
        "--disable-breakpad",
        "--disable-features=msEdgeSidebarV2,msUndersideButton,OptimizationGuideModelDownloading,Translate,AutofillServerCommunication",
        "--no-first-run",
        "--no-default-browser-check",
        "--no-sandbox",
        f"--user-data-dir={profile_dir.as_posix()}",
        f"--window-size={width},{height}",
        f"--virtual-time-budget={max(1000, int(budget_ms))}",
    ]


def edge_shot(edge_path: Path, url: str, shot_path: Path, *, profile_dir: Path, width: int = 1680, height: int = 1200, budget_ms: int = 26000) -> None:
    shot_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = edge_cmd(edge_path, profile_dir, width, height, budget_ms) + [f"--screenshot={shot_path.as_posix()}", url]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=180)
    if proc.returncode != 0:
        raise RuntimeError(f"edge screenshot failed: {proc.stderr}")


def edge_dom(edge_path: Path, url: str, *, profile_dir: Path, width: int = 1680, height: int = 1200, budget_ms: int = 26000) -> str:
    cmd = edge_cmd(edge_path, profile_dir, width, height, budget_ms) + ["--dump-dom", url]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=180)
    if proc.returncode != 0:
        raise RuntimeError(f"edge dump-dom failed: {proc.stderr}")
    return proc.stdout


def parse_probe(dom_text: str) -> dict[str, Any]:
    matched = re.search(r"<pre[^>]*id=['\"]defectCenterProbeOutput['\"][^>]*>(.*?)</pre>", str(dom_text or ""), flags=re.I | re.S)
    if not matched:
        raise RuntimeError("defectCenterProbeOutput_not_found")
    raw = html.unescape(matched.group(1) or "").strip()
    if not raw:
        raise RuntimeError("defectCenterProbeOutput_empty")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise RuntimeError("defectCenterProbeOutput_not_dict")
    return payload


def defect_probe_url(base_url: str, case_id: str, extra: dict[str, str] | None = None) -> str:
    query: dict[str, str] = {
        "defect_probe": "1",
        "defect_probe_case": str(case_id),
        "_ts": str(int(time.time() * 1000)),
    }
    if extra:
        for key, value in extra.items():
            query[str(key)] = str(value)
    return base_url.rstrip("/") + "/?" + urlencode(query)


def capture_probe(edge_path: Path, base_url: str, evidence_root: Path, name: str, case_id: str, extra: dict[str, str] | None = None) -> tuple[str, str, dict[str, Any]]:
    url = defect_probe_url(base_url, case_id, extra)
    shot_path = evidence_root / "screenshots" / f"{name}.png"
    probe_path = evidence_root / "screenshots" / f"{name}.probe.json"
    profile_dir = evidence_root / "edge-profile" / name
    edge_shot(edge_path, url, shot_path, profile_dir=profile_dir)
    probe = parse_probe(edge_dom(edge_path, url, profile_dir=profile_dir))
    write_json(probe_path, probe)
    return shot_path.as_posix(), probe_path.as_posix(), probe


def capture_probe_with_retry(
    edge_path: Path,
    base_url: str,
    evidence_root: Path,
    name: str,
    case_id: str,
    extra: dict[str, str] | None = None,
    *,
    attempts: int = 3,
    retry_delay_s: float = 1.0,
) -> tuple[str, str, dict[str, Any]]:
    last_error: Exception | None = None
    last_result: tuple[str, str, dict[str, Any]] | None = None
    for attempt in range(max(1, attempts)):
        try:
            result = capture_probe(edge_path, base_url, evidence_root, name, case_id, extra)
            last_result = result
            if bool((result[2] or {}).get("pass")):
                return result
        except Exception as exc:
            last_error = exc
        if attempt + 1 < max(1, attempts):
            time.sleep(retry_delay_s)
    if last_result is not None:
        return last_result
    assert last_error is not None
    raise last_error


def launch_server(workspace_root: Path, runtime_root: Path, *, host: str, port: int, stdout_path: Path, stderr_path: Path) -> tuple[subprocess.Popen[bytes], Any, Any]:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_handle = stdout_path.open("wb")
    stderr_handle = stderr_path.open("wb")
    env = os.environ.copy()
    env["WORKFLOW_RUNTIME_ENV"] = "test"
    server = subprocess.Popen(
        [sys.executable, "scripts/workflow_web_server.py", "--root", str(runtime_root), "--host", host, "--port", str(port)],
        cwd=str(workspace_root),
        stdout=stdout_handle,
        stderr=stderr_handle,
        env=env,
    )
    return server, stdout_handle, stderr_handle


def stop_server(server: subprocess.Popen[bytes], stdout_handle: Any, stderr_handle: Any) -> None:
    try:
        server.terminate()
        server.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait(timeout=10)
    finally:
        stdout_handle.close()
        stderr_handle.close()


@contextmanager
def running_server(workspace_root: Path, runtime_root: Path, *, host: str, port: int, stdout_path: Path, stderr_path: Path) -> Iterator[None]:
    server, stdout_handle, stderr_handle = launch_server(
        workspace_root,
        runtime_root,
        host=host,
        port=port,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
    )
    try:
        yield
    finally:
        stop_server(server, stdout_handle, stderr_handle)


def seed_defect_flow(base_url: str, evidence_root: Path) -> dict[str, Any]:
    api_root = evidence_root / "api"
    status, formal_submit = api_request(
        base_url,
        "POST",
        "/api/defects",
        {
            "defect_summary": "升级后工作区路径被刷掉",
            "report_text": "升级完成后工作区路径丢失，进度条回退并且显示异常，属于 workflow 自身问题。",
            "evidence_images": [{"name": "formal.png", "url": IMAGE_DATA_URL}],
            "automation_context": {"suite_id": "defect-center", "case_id": "formal", "run_id": "browser-ac", "env": "test"},
            "is_test_data": True,
            "operator": "acceptance",
        },
    )
    assert_true(status == 200 and formal_submit.get("ok"), "formal defect submit failed")
    write_json(api_root / "submit-formal.json", formal_submit)
    formal_report = dict(formal_submit.get("report") or {})
    formal_id = str(formal_report.get("report_id") or "").strip()
    assert_true(formal_id != "", "formal report_id missing")

    status, process_result = api_request(
        base_url,
        "POST",
        f"/api/defects/{formal_id}/process-task",
        {"operator": "acceptance"},
        timeout_s=240,
    )
    assert_true(status == 200 and process_result.get("ok"), "process task create failed")
    write_json(api_root / "process-task.json", process_result)

    status, resolved_result = api_request(
        base_url,
        "POST",
        f"/api/defects/{formal_id}/resolved-version",
        {"resolved_version": "20260322-browser-ac", "operator": "acceptance"},
    )
    assert_true(status == 200 and resolved_result.get("ok"), "resolved version writeback failed")
    write_json(api_root / "resolved-version.json", resolved_result)

    status, not_formal_submit = api_request(
        base_url,
        "POST",
        "/api/defects",
        {
            "defect_summary": "希望训练入口文案更短",
            "report_text": "这里更像是文案优化建议，不是确定性的 workflow 缺陷。",
            "evidence_images": [{"name": "suggestion.png", "url": IMAGE_DATA_URL}],
            "automation_context": {"suite_id": "defect-center", "case_id": "not-formal", "run_id": "browser-ac", "env": "test"},
            "is_test_data": True,
            "operator": "acceptance",
        },
    )
    assert_true(status == 200 and not_formal_submit.get("ok"), "not formal submit failed")
    write_json(api_root / "submit-not-formal.json", not_formal_submit)
    dispute_report = dict(not_formal_submit.get("report") or {})
    dispute_id = str(dispute_report.get("report_id") or "").strip()
    assert_true(dispute_id != "", "dispute report_id missing")

    status, supplement_text = api_request(base_url, "POST", f"/api/defects/{dispute_id}/supplements/text", {"text": "补充说明：该现象已经影响缺陷判断。", "operator": "acceptance"})
    assert_true(status == 200 and supplement_text.get("ok"), "supplement text failed")
    write_json(api_root / "dispute-supplement-text.json", supplement_text)

    status, supplement_images = api_request(base_url, "POST", f"/api/defects/{dispute_id}/supplements/images", {"evidence_images": [{"name": "dispute.png", "url": IMAGE_DATA_URL}], "operator": "acceptance"})
    assert_true(status == 200 and supplement_images.get("ok"), "supplement images failed")
    write_json(api_root / "dispute-supplement-images.json", supplement_images)

    status, dispute_mark = api_request(base_url, "POST", f"/api/defects/{dispute_id}/dispute", {"reason": "补充后仍认为应进入复核。", "operator": "acceptance"})
    assert_true(status == 200 and dispute_mark.get("ok"), "dispute mark failed")
    write_json(api_root / "dispute-mark.json", dispute_mark)

    status, review_result = api_request(
        base_url,
        "POST",
        f"/api/defects/{dispute_id}/review-task",
        {"operator": "acceptance"},
        timeout_s=240,
    )
    assert_true(status == 200 and review_result.get("ok"), "review task create failed")
    write_json(api_root / "review-task.json", review_result)

    status, list_payload = api_request(base_url, "GET", "/api/defects?status=all&keyword=path")
    assert_true(status == 200 and list_payload.get("ok"), "defect list read failed")
    write_json(api_root / "defect-list.json", list_payload)

    status, formal_detail = api_request(base_url, "GET", f"/api/defects/{formal_id}")
    assert_true(status == 200 and formal_detail.get("ok"), "formal detail read failed")
    write_json(api_root / "formal-detail.json", formal_detail)

    status, dispute_detail = api_request(base_url, "GET", f"/api/defects/{dispute_id}")
    assert_true(status == 200 and dispute_detail.get("ok"), "dispute detail read failed")
    write_json(api_root / "dispute-detail.json", dispute_detail)

    status, dispute_history = api_request(base_url, "GET", f"/api/defects/{dispute_id}/history")
    assert_true(status == 200 and dispute_history.get("ok"), "dispute history read failed")
    write_json(api_root / "dispute-history.json", dispute_history)

    return {
        "formal_id": formal_id,
        "formal_dts_id": str((formal_detail.get("report") or {}).get("dts_id") or "").strip(),
        "dispute_id": dispute_id,
    }


def main() -> int:
    args = parse_args()
    workspace_root = Path(args.root).resolve()
    artifacts_root = Path(args.artifacts_dir).resolve() / "defect-center-browser"
    logs_root = Path(args.logs_dir).resolve() / "defect-center-browser"
    if artifacts_root.exists():
        shutil.rmtree(artifacts_root, ignore_errors=True)
    if logs_root.exists():
        shutil.rmtree(logs_root, ignore_errors=True)
    artifacts_root.mkdir(parents=True, exist_ok=True)
    logs_root.mkdir(parents=True, exist_ok=True)
    runtime_root = Path(os.getenv("TEST_TMP_DIR") or (artifacts_root / "runtime")).resolve()
    if runtime_root.exists():
        shutil.rmtree(runtime_root)
    runtime_root, bootstrap_cfg = prepare_isolated_runtime_root(workspace_root, runtime_root)
    edge_path = find_edge()
    base_url = f"http://{args.host}:{int(args.port)}"
    with running_server(
        workspace_root,
        runtime_root,
        host=args.host,
        port=int(args.port),
        stdout_path=logs_root / "server.stdout.log",
        stderr_path=logs_root / "server.stderr.log",
    ):
        health = wait_for_health(base_url)
        seeded = seed_defect_flow(base_url, artifacts_root)
        screenshots: dict[str, Any] = {}
        for name, case_id, extra in (
            ("requirement-empty", "requirement_empty", {}),
            ("defect-main", "main", {"defect_probe_report": seeded["formal_id"]}),
            ("defect-dispute", "dispute", {"defect_probe_report": seeded["dispute_id"]}),
            ("defect-dispute-supplement", "dispute_supplement", {"defect_probe_report": seeded["dispute_id"]}),
            ("defect-review-input", "review_input", {"defect_probe_report": seeded["formal_id"]}),
            ("defect-filter-search", "filter_search", {"defect_probe_report": seeded["formal_id"], "defect_probe_status": "resolved", "defect_probe_keyword": seeded["formal_dts_id"]}),
        ):
            shot_path, probe_path, probe = capture_probe_with_retry(edge_path, base_url, artifacts_root, name, case_id, extra)
            assert_true(bool(probe.get("pass")), f"probe failed: {case_id}")
            screenshots[name] = {
                "case": case_id,
                "screenshot": shot_path,
                "probe": probe_path,
                "probe_payload": probe,
            }
        summary = {
            "ok": True,
            "base_url": base_url,
            "health": health,
            "bootstrap_cfg": bootstrap_cfg,
            "seeded": seeded,
            "screenshots": screenshots,
        }
        write_json(artifacts_root / "summary.json", summary)
        print((artifacts_root / "summary.json").as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
