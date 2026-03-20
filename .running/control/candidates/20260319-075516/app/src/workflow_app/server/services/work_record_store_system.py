from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from . import work_record_store_index as _record_index
from .work_record_store import (
    _STORE_LOCK,
    _SCHEMA_VERSION,
    _append_jsonl,
    _append_markdown,
    _load_json_dict,
    _load_jsonl,
    _normalize_bool,
    _now_ts,
    _write_json,
    _write_jsonl,
    change_log_path,
    ensure_store,
    failure_cases_path,
    ingress_requests_path,
    list_session_records,
    message_delete_audit_path,
    normalize_work_record_ref,
    policy_confirmation_audit_path,
    policy_patch_task_path,
    policy_patch_tasks_root,
    reconcile_runs_path,
    system_runs_root,
    web_e2e_path,
    workflow_events_path,
)


def _write_system_run_stub(path: Path, payload: dict[str, Any]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# 系统运行记录", ""]
    for key in ("run_id", "run_at", "reason", "status", "notes"):
        value = str(payload.get(key) or "").strip()
        if value:
            lines.append(f"- {key}: {value}")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def append_message_delete_audit_record(root: Path, payload: dict[str, Any]) -> int:
    ensure_store(root)
    with _STORE_LOCK:
        rows = _load_jsonl(message_delete_audit_path(root))
        audit_id = len(rows) + 1
        row = dict(payload or {})
        row["ref"] = normalize_work_record_ref(root, str(row.get("ref") or ""))
        row["audit_id"] = audit_id
        rows.append(row)
        _write_jsonl(message_delete_audit_path(root), rows)
        _record_index.sync_audit_and_system_indexes(root)
        return audit_id


def append_policy_confirmation_audit_record(root: Path, payload: dict[str, Any]) -> int:
    ensure_store(root)
    with _STORE_LOCK:
        rows = _load_jsonl(policy_confirmation_audit_path(root))
        audit_id = len(rows) + 1
        row = dict(payload or {})
        row["ref"] = normalize_work_record_ref(root, str(row.get("ref") or ""))
        row["audit_id"] = audit_id
        rows.append(row)
        _write_jsonl(policy_confirmation_audit_path(root), rows)
        _record_index.sync_audit_and_system_indexes(root)
        return audit_id


def create_policy_patch_task_record(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    ensure_store(root)
    patch_task_id = str(payload.get("patch_task_id") or "").strip()
    if not patch_task_id:
        raise RuntimeError("patch_task_id required")
    record = {"record_type": "policy_patch_task", "schema_version": _SCHEMA_VERSION, **dict(payload or {})}
    _write_json(policy_patch_task_path(root, patch_task_id), record)
    _record_index.sync_policy_patch_task(root, patch_task_id)
    return record


def list_policy_patch_task_records(root: Path, limit: int = 200) -> list[dict[str, Any]]:
    ensure_store(root)
    rows = _record_index.list_policy_patch_task_records_from_index(root, limit=limit)
    if rows:
        return rows
    fallback = [
        _load_json_dict(path)
        for path in sorted(policy_patch_tasks_root(root).glob("*.json"), key=lambda item: item.as_posix().lower())
    ]
    fallback = [row for row in fallback if row]
    fallback.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
    return fallback[: max(1, min(int(limit), 2000))]


def latest_policy_patch_task_for_session(root: Path, session_id: str) -> str:
    lookup = str(session_id or "").strip()
    for row in list_policy_patch_task_records(root, limit=20000):
        if str(row.get("source_session_id") or "") == lookup:
            return str(row.get("patch_task_id") or "")
    return ""


def policy_closure_stats_record(root: Path) -> dict[str, Any]:
    confirmations = _load_jsonl(policy_confirmation_audit_path(root))
    patches = list_policy_patch_task_records(root, limit=20000)
    sessions = list_session_records(root, include_test_data=True, limit=20000)
    triggered = len(confirmations)
    rejected = len([row for row in confirmations if str(row.get("action") or "") == "reject"])
    manual = len([row for row in confirmations if _normalize_bool(row.get("manual_fallback"))])
    patch_total = len(patches)
    patch_done = len([row for row in patches if str(row.get("status") or "") == "done"])
    denominator = max(1, len(sessions) + rejected)
    return {
        "fallback_triggered": triggered,
        "fallback_trigger_rate_pct": round((triggered / denominator) * 100.0, 2),
        "manual_fallback_triggered": manual,
        "manual_fallback_rate_pct": round((manual / denominator) * 100.0, 2),
        "manual_fallback_usage_alert": bool(manual / denominator >= 0.3),
        "patch_task_total": patch_total,
        "patch_task_done": patch_done,
        "patch_completion_rate_pct": round((patch_done / max(1, patch_total)) * 100.0, 2) if patch_total else 0.0,
        "created_sessions": len(sessions),
        "rejected_confirmations": rejected,
    }


def append_workflow_event_log_record(root: Path, payload: dict[str, Any]) -> None:
    ensure_store(root)
    row = dict(payload or {})
    row["ref"] = normalize_work_record_ref(root, str(row.get("ref") or ""))
    _append_jsonl(workflow_events_path(root), row)
    _record_index.sync_audit_and_system_indexes(root)


def list_workflow_event_log_records(root: Path) -> list[dict[str, Any]]:
    ensure_store(root)
    return _load_jsonl(workflow_events_path(root))


def append_change_log_record(root: Path, title: str, detail: str) -> None:
    _append_markdown(change_log_path(root), "# Change Log", [f"## {_now_ts()} - {title}", f"- {detail}"])


def append_failure_case_record(root: Path, title: str, detail: str) -> None:
    _append_markdown(failure_cases_path(root), "# Failure Cases", [f"## {_now_ts()} - {title}", f"- detail: {detail}"])


def append_web_e2e_record(root: Path, lines: list[str]) -> str:
    _append_markdown(web_e2e_path(root), "# Web E2E", lines)
    return web_e2e_path(root).as_posix()


def unique_system_run_path(root: Path, prefix: str) -> Path:
    ts = datetime.now().astimezone()
    path = system_runs_root(root) / f"{prefix}-{ts.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def record_ingress_request(root: Path, payload: dict[str, Any]) -> None:
    ensure_store(root)
    with _STORE_LOCK:
        current = _load_json_dict(ingress_requests_path(root))
        items = current.get("items") if isinstance(current.get("items"), dict) else {}
        request_id = str(payload.get("request_id") or "").strip()
        if request_id:
            items[request_id] = dict(payload or {})
        _write_json(ingress_requests_path(root), {"updated_at": _now_ts(), "items": items})


def mark_ingress_request_logged(root: Path, request_id: str) -> None:
    ensure_store(root)
    with _STORE_LOCK:
        current = _load_json_dict(ingress_requests_path(root))
        items = current.get("items") if isinstance(current.get("items"), dict) else {}
        row = dict(items.get(str(request_id or "").strip()) or {})
        if row:
            row["event_logged"] = 1
            items[str(request_id or "").strip()] = row
            _write_json(ingress_requests_path(root), {"updated_at": _now_ts(), "items": items})


def list_ingress_request_records(root: Path) -> list[dict[str, Any]]:
    current = _load_json_dict(ingress_requests_path(root))
    items = current.get("items") if isinstance(current.get("items"), dict) else {}
    rows = [dict(item) for item in items.values()]
    rows.sort(key=lambda item: str(item.get("created_at") or ""))
    return rows


def append_reconcile_run_record(root: Path, payload: dict[str, Any]) -> None:
    ensure_store(root)
    row = dict(payload or {})
    row["ref"] = normalize_work_record_ref(root, str(row.get("ref") or ""))
    _append_jsonl(reconcile_runs_path(root), row)
    ref = str(row.get("ref") or "")
    if ref:
        ref_path = Path(ref)
        if ref_path.suffix.lower() == ".md":
            _write_system_run_stub(
                ref_path,
                row,
            )
    _record_index.sync_audit_and_system_indexes(root)


def latest_reconcile_run_record(root: Path) -> dict[str, Any] | None:
    rows = _load_jsonl(reconcile_runs_path(root))
    return rows[-1] if rows else None
