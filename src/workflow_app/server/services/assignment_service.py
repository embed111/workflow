from __future__ import annotations

import json
import re
import sqlite3
import uuid
from pathlib import Path
from typing import Any


def bind_runtime_symbols(symbols: dict[str, object]) -> None:
    if not isinstance(symbols, dict):
        return
    target = globals()
    module_name = str(target.get("__name__") or "")
    for key, value in symbols.items():
        if str(key).startswith("__"):
            continue
        current = target.get(key)
        if callable(current) and getattr(current, "__module__", "") == module_name:
            continue
        target[key] = value


DEFAULT_ASSIGNMENT_CONCURRENCY_LIMIT = 5
ASSIGNMENT_REVIEW_MODES = {"none", "partial", "full"}
ASSIGNMENT_NODE_STATUSES = {"pending", "ready", "running", "succeeded", "failed", "blocked"}
ASSIGNMENT_NONTERMINAL_STATUSES = {"pending", "ready", "blocked"}
ASSIGNMENT_SCHEDULER_STATES = {"idle", "running", "pause_pending", "paused"}
ASSIGNMENT_DELIVERY_MODES = {"none", "specified"}
ASSIGNMENT_ARTIFACT_DELIVERY_STATUSES = {"pending", "delivered"}
ASSIGNMENT_TEST_GRAPH_SOURCE = "assignment-prototype-test-data"
ASSIGNMENT_TEST_GRAPH_EXTERNAL_REQUEST_ID = "task-center-prototype-v1"
ASSIGNMENT_TEST_GRAPH_NAME = "任务中心原型测试图"
ASSIGNMENT_TEST_GRAPH_SUMMARY = "基于任务中心参考图生成的测试任务图"
ASSIGNMENT_TEST_GRAPH_CREATED_AT = "2026-03-14T09:40:00+08:00"
ASSIGNMENT_TEST_GRAPH_UPDATED_AT = "2026-03-14T12:20:30+08:00"


class AssignmentCenterError(RuntimeError):
    def __init__(
        self,
        status_code: int,
        message: str,
        code: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.extra = dict(extra or {})


def assignment_ticket_id() -> str:
    ts = now_local()
    return f"asg-{date_key(ts)}-{ts.strftime('%H%M%S')}-{uuid.uuid4().hex[:6]}"


def assignment_node_id() -> str:
    ts = now_local()
    return f"node-{date_key(ts)}-{ts.strftime('%H%M%S')}-{uuid.uuid4().hex[:6]}"


def assignment_audit_id() -> str:
    ts = now_local()
    return f"aaud-{date_key(ts)}-{ts.strftime('%H%M%S')}-{uuid.uuid4().hex[:6]}"


def _db_ref(audit_id: str) -> str:
    return f"state/workflow.db#assignment_audit_log/{audit_id}"


def _row_dict(row: sqlite3.Row | None) -> dict[str, Any]:
    if row is None:
        return {}
    return {name: row[name] for name in row.keys()}


def _json_load(raw: object, fallback: Any) -> Any:
    if raw in (None, ""):
        return fallback
    try:
        payload = json.loads(str(raw))
    except Exception:
        return fallback
    return payload


def _normalize_text(raw: Any, *, field: str, required: bool = False, max_len: int = 5000) -> str:
    text = str(raw or "").strip()
    if required and not text:
        raise AssignmentCenterError(400, f"{field} required", f"{field}_required")
    if len(text) > max_len:
        raise AssignmentCenterError(
            400,
            f"{field} too long",
            f"{field}_too_long",
            {"max_length": max_len},
        )
    return text


def _normalize_positive_int(
    raw: Any,
    *,
    field: str,
    default: int,
    minimum: int = 1,
    maximum: int = 64,
) -> int:
    if raw in (None, ""):
        value = int(default)
    else:
        try:
            value = int(raw)
        except Exception as exc:
            raise AssignmentCenterError(400, f"{field} invalid", f"{field}_invalid") from exc
    if value < minimum or value > maximum:
        raise AssignmentCenterError(
            400,
            f"{field} out of range",
            f"{field}_out_of_range",
            {"minimum": minimum, "maximum": maximum},
        )
    return value


def normalize_assignment_priority(raw: Any, *, required: bool = True) -> int:
    if raw in (None, ""):
        if required:
            raise AssignmentCenterError(400, "priority required", "priority_required")
        return 1
    if isinstance(raw, (int, float)):
        value = int(raw)
    else:
        text = str(raw or "").strip().upper()
        if not text:
            if required:
                raise AssignmentCenterError(400, "priority required", "priority_required")
            return 1
        if text.startswith("P") and len(text) == 2 and text[1].isdigit():
            value = int(text[1])
        else:
            try:
                value = int(text)
            except Exception as exc:
                raise AssignmentCenterError(
                    400,
                    "priority only allows P0/P1/P2/P3 or 0/1/2/3",
                    "priority_invalid",
                ) from exc
    if value not in (0, 1, 2, 3):
        raise AssignmentCenterError(
            400,
            "priority only allows P0/P1/P2/P3 or 0/1/2/3",
            "priority_invalid",
        )
    return value


def assignment_priority_label(value: Any) -> str:
    try:
        num = int(value)
    except Exception:
        num = 1
    if num not in (0, 1, 2, 3):
        num = 1
    return f"P{num}"


def _normalize_delivery_mode(raw: Any) -> str:
    value = str(raw or "none").strip().lower() or "none"
    if value not in ASSIGNMENT_DELIVERY_MODES:
        raise AssignmentCenterError(
            400,
            "delivery_mode invalid",
            "delivery_mode_invalid",
            {"allowed": sorted(ASSIGNMENT_DELIVERY_MODES)},
        )
    return value


def _delivery_mode_text(value: Any) -> str:
    return "指定交付人" if str(value or "").strip().lower() == "specified" else "无交付人"


def _artifact_delivery_status_text(value: Any) -> str:
    return "已交付" if str(value or "").strip().lower() == "delivered" else "待交付"


def _normalize_artifact_delivery_status(raw: Any) -> str:
    value = str(raw or "pending").strip().lower() or "pending"
    if value not in ASSIGNMENT_ARTIFACT_DELIVERY_STATUSES:
        raise AssignmentCenterError(
            400,
            "artifact_delivery_status invalid",
            "artifact_delivery_status_invalid",
            {"allowed": sorted(ASSIGNMENT_ARTIFACT_DELIVERY_STATUSES)},
        )
    return value


def _normalize_review_mode(raw: Any) -> str:
    value = str(raw or "none").strip().lower() or "none"
    if value not in ASSIGNMENT_REVIEW_MODES:
        raise AssignmentCenterError(
            400,
            "review_mode invalid",
            "review_mode_invalid",
            {"allowed": sorted(ASSIGNMENT_REVIEW_MODES)},
        )
    if value != "none":
        raise AssignmentCenterError(
            409,
            "review_mode not supported in phase1",
            "not_supported_in_phase1",
            {"review_mode": value},
        )
    return value


def _normalize_status(raw: Any, *, field: str = "status") -> str:
    value = str(raw or "").strip().lower()
    if value not in ASSIGNMENT_NODE_STATUSES:
        raise AssignmentCenterError(
            400,
            f"{field} invalid",
            f"{field}_invalid",
            {"allowed": sorted(ASSIGNMENT_NODE_STATUSES)},
        )
    return value


def _normalize_scheduler_state(raw: Any) -> str:
    value = str(raw or "").strip().lower()
    if value not in ASSIGNMENT_SCHEDULER_STATES:
        raise AssignmentCenterError(
            400,
            "scheduler_state invalid",
            "scheduler_state_invalid",
            {"allowed": sorted(ASSIGNMENT_SCHEDULER_STATES)},
        )
    return value


def _normalize_assignment_test_flag(raw: Any, *, default: bool = False) -> bool:
    if raw in (None, ""):
        return bool(default)
    try:
        return bool(parse_bool_flag(raw, default=default))
    except Exception:
        return bool(default)


def _row_is_test_data(row: sqlite3.Row | dict[str, Any] | None) -> bool:
    if row is None:
        return False
    try:
        raw = row["is_test_data"]  # type: ignore[index]
    except Exception:
        raw = row.get("is_test_data") if isinstance(row, dict) else 0
    return _normalize_assignment_test_flag(raw, default=False)


def _scheduler_state_text(value: str) -> str:
    key = str(value or "").strip().lower()
    if key == "running":
        return "运行中"
    if key == "pause_pending":
        return "暂停中"
    if key == "paused":
        return "已暂停"
    return "未启动"


def _node_status_text(value: str) -> str:
    key = str(value or "").strip().lower()
    mapping = {
        "pending": "待开始",
        "ready": "待开始",
        "running": "进行中",
        "succeeded": "已完成",
        "failed": "失败",
        "blocked": "阻塞",
    }
    return mapping.get(key, key or "-")


def _safe_json_list(raw: Any) -> list[Any]:
    if isinstance(raw, list):
        return list(raw)
    if raw in (None, ""):
        return []
    payload = _json_load(raw, [])
    return payload if isinstance(payload, list) else []


def _dedupe_tokens(values: list[Any], *, allow_empty: bool = False) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in values:
        token = safe_token(str(raw or ""), "", 160)
        if not token and not allow_empty:
            continue
        if token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def _default_assignment_operator(raw: Any) -> str:
    return safe_token(str(raw or "web-user"), "web-user", 80)


def _ensure_graph_row(conn: sqlite3.Connection, ticket_id: str) -> sqlite3.Row:
    row = conn.execute(
        """
        SELECT
            ticket_id,graph_name,source_workflow,summary,review_mode,
            global_concurrency_limit,is_test_data,external_request_id,scheduler_state,pause_note,
            created_at,updated_at
        FROM assignment_graphs
        WHERE ticket_id=?
        LIMIT 1
        """,
        (ticket_id,),
    ).fetchone()
    if row is None:
        raise AssignmentCenterError(
            404,
            "assignment graph not found",
            "assignment_graph_not_found",
            {"ticket_id": ticket_id},
        )
    return row


def _ensure_graph_row_visible(
    conn: sqlite3.Connection,
    ticket_id: str,
    *,
    include_test_data: bool,
) -> sqlite3.Row:
    row = _ensure_graph_row(conn, ticket_id)
    if _row_is_test_data(row) and not include_test_data:
        raise AssignmentCenterError(
            404,
            "assignment graph not found",
            "assignment_graph_not_found",
            {"ticket_id": ticket_id},
        )
    return row


def _ensure_setting_row(
    conn: sqlite3.Connection,
    *,
    key: str,
    default_value: str,
    now_text: str,
) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO assignment_system_settings (
            setting_key,setting_value,updated_at
        ) VALUES (?,?,?)
        """,
        (key, default_value, now_text),
    )


def _get_global_concurrency_limit(conn: sqlite3.Connection) -> tuple[int, str]:
    now_text = iso_ts(now_local())
    _ensure_setting_row(
        conn,
        key="global_concurrency_limit",
        default_value=str(DEFAULT_ASSIGNMENT_CONCURRENCY_LIMIT),
        now_text=now_text,
    )
    row = conn.execute(
        """
        SELECT setting_value,updated_at
        FROM assignment_system_settings
        WHERE setting_key='global_concurrency_limit'
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        return DEFAULT_ASSIGNMENT_CONCURRENCY_LIMIT, now_text
    try:
        value = int(str(row["setting_value"] or DEFAULT_ASSIGNMENT_CONCURRENCY_LIMIT))
    except Exception:
        value = DEFAULT_ASSIGNMENT_CONCURRENCY_LIMIT
    if value < 1:
        value = DEFAULT_ASSIGNMENT_CONCURRENCY_LIMIT
    return value, str(row["updated_at"] or now_text)


def get_assignment_concurrency_settings(root: Path) -> dict[str, Any]:
    conn = connect_db(root)
    try:
        limit, updated_at = _get_global_concurrency_limit(conn)
        conn.commit()
    finally:
        conn.close()
    return {
        "global_concurrency_limit": int(limit),
        "updated_at": updated_at,
    }


def set_assignment_concurrency_settings(
    root: Path,
    *,
    global_concurrency_limit: Any,
    operator: str,
) -> dict[str, Any]:
    now_text = iso_ts(now_local())
    next_limit = _normalize_positive_int(
        global_concurrency_limit,
        field="global_concurrency_limit",
        default=DEFAULT_ASSIGNMENT_CONCURRENCY_LIMIT,
        minimum=1,
        maximum=64,
    )
    operator_text = _default_assignment_operator(operator)
    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_setting_row(
            conn,
            key="global_concurrency_limit",
            default_value=str(DEFAULT_ASSIGNMENT_CONCURRENCY_LIMIT),
            now_text=now_text,
        )
        conn.execute(
            """
            UPDATE assignment_system_settings
            SET setting_value=?,updated_at=?
            WHERE setting_key='global_concurrency_limit'
            """,
            (str(next_limit), now_text),
        )
        audit_id = _write_assignment_audit(
            conn,
            ticket_id="",
            node_id="",
            action="update_concurrency_limit",
            operator=operator_text,
            reason=f"set global_concurrency_limit={next_limit}",
            target_status="",
            detail={"global_concurrency_limit": next_limit},
            created_at=now_text,
        )
        conn.commit()
    finally:
        conn.close()
    return {
        "global_concurrency_limit": next_limit,
        "updated_at": now_text,
        "audit_id": audit_id,
    }


def _write_assignment_audit(
    conn: sqlite3.Connection,
    *,
    ticket_id: str,
    node_id: str,
    action: str,
    operator: str,
    reason: str,
    target_status: str,
    detail: dict[str, Any] | None,
    created_at: str,
) -> str:
    audit_id = assignment_audit_id()
    conn.execute(
        """
        INSERT INTO assignment_audit_log (
            audit_id,ticket_id,node_id,action,operator,reason,target_status,detail_json,ref,created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
        (
            audit_id,
            str(ticket_id or "").strip(),
            str(node_id or "").strip(),
            str(action or "").strip(),
            _default_assignment_operator(operator),
            str(reason or "").strip(),
            str(target_status or "").strip(),
            json.dumps(detail or {}, ensure_ascii=False),
            _db_ref(audit_id),
            created_at,
        ),
    )
    return audit_id


def _assignment_artifact_root(root: Path) -> Path:
    runtime_cfg = load_runtime_config(root)
    raw = str(runtime_cfg.get("artifact_root") or "").strip()
    base = Path(__file__).resolve().parents[4]
    default_root = (base.parent / ".output").resolve(strict=False)
    try:
        candidate = normalize_abs_path(raw, base=base) if raw else default_root
    except Exception:
        candidate = default_root
    artifact_root, _workspace_root = ensure_artifact_root_dirs(candidate)
    return artifact_root


def _assignment_workspace_root(root: Path) -> Path:
    artifact_root = _assignment_artifact_root(root)
    return (artifact_root / "workspace" / "assignments").resolve(strict=False)


def _normalize_path_segment(raw: Any, fallback: str) -> str:
    text = str(raw or "").strip()
    if not text:
        text = str(fallback or "").strip()
    if not text:
        text = "item"
    text = re.sub('[<>:"/\\\\|?*\\x00-\\x1f]+', "_", text).strip().strip(".")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:96] or "item"


def _artifact_label_file_name(node: dict[str, Any]) -> str:
    label = (
        str(node.get("expected_artifact") or "").strip()
        or str(node.get("node_name") or "").strip()
        or str(node.get("node_id") or "").strip()
        or "artifact"
    )
    return _normalize_path_segment(label, "artifact") + ".md"


def _node_artifact_file_paths(root: Path, node: dict[str, Any]) -> list[Path]:
    artifact_root = _assignment_artifact_root(root)
    task_dir = _normalize_path_segment(
        node.get("node_name") or node.get("node_id") or "task",
        "task",
    )
    worker_name = _normalize_path_segment(
        node.get("assigned_agent_name") or node.get("assigned_agent_id") or "agent",
        "agent",
    )
    file_name = _artifact_label_file_name(node)
    paths = [artifact_root / worker_name / "product" / task_dir / file_name]
    if str(node.get("delivery_mode") or "").strip().lower() == "specified":
        receiver_name = _normalize_path_segment(
            node.get("delivery_receiver_agent_name") or node.get("delivery_receiver_agent_id") or "receiver",
            "receiver",
        )
        receiver_path = artifact_root / receiver_name / "receive" / task_dir / file_name
        if receiver_path not in paths:
            paths.append(receiver_path)
    return paths


def _assignment_ticket_workspace_dir(root: Path, ticket_id: str) -> Path:
    return _assignment_workspace_root(root) / str(ticket_id or "").strip()


def _assignment_graph_record_path(root: Path, ticket_id: str) -> Path:
    return _assignment_ticket_workspace_dir(root, ticket_id) / "graph.json"


def _assignment_node_record_path(root: Path, ticket_id: str, node_id: str) -> Path:
    return _assignment_ticket_workspace_dir(root, ticket_id) / "nodes" / (str(node_id or "").strip() + ".json")


def _write_assignment_workspace_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _persist_assignment_workspace_graph(
    root: Path,
    *,
    snapshot: dict[str, Any],
    record_state: str = "active",
    extra: dict[str, Any] | None = None,
) -> str:
    graph_row = snapshot.get("graph_row")
    if not graph_row:
        return ""
    graph_overview = _graph_overview_payload(
        graph_row,
        metrics_summary=snapshot.get("metrics_summary") or {},
        scheduler_state_payload=snapshot.get("scheduler") or {},
    )
    ticket_id = str(graph_overview.get("ticket_id") or "").strip()
    if not ticket_id:
        return ""
    path = _assignment_graph_record_path(root, ticket_id)
    payload = {
        "record_type": "assignment_graph",
        "record_state": str(record_state or "active"),
        "artifact_root": str(_assignment_artifact_root(root)),
        "workspace_root": str(_assignment_workspace_root(root)),
        "ticket_id": ticket_id,
        "is_test_data": bool(graph_overview.get("is_test_data")),
        "graph_name": str(graph_overview.get("graph_name") or "").strip(),
        "source_workflow": str(graph_overview.get("source_workflow") or "").strip(),
        "summary": str(graph_overview.get("summary") or "").strip(),
        "scheduler_state": str(graph_overview.get("scheduler_state") or "").strip(),
        "scheduler_state_text": str(graph_overview.get("scheduler_state_text") or "").strip(),
        "metrics_summary": snapshot.get("metrics_summary") or {},
        "created_at": str(graph_overview.get("created_at") or "").strip(),
        "updated_at": str(graph_overview.get("updated_at") or "").strip(),
    }
    if isinstance(extra, dict) and extra:
        payload["extra"] = dict(extra)
    _write_assignment_workspace_json(path, payload)
    return str(path)


def _persist_assignment_workspace_node(
    root: Path,
    *,
    node: dict[str, Any],
    record_state: str = "active",
    audit_id: str = "",
    extra: dict[str, Any] | None = None,
) -> str:
    ticket_id = str(node.get("ticket_id") or "").strip()
    node_id = str(node.get("node_id") or "").strip()
    if not ticket_id or not node_id:
        return ""
    path = _assignment_node_record_path(root, ticket_id, node_id)
    payload = {
        "record_type": "assignment_node",
        "record_state": str(record_state or "active"),
        "artifact_root": str(_assignment_artifact_root(root)),
        "workspace_root": str(_assignment_workspace_root(root)),
        "ticket_id": ticket_id,
        "is_test_data": bool(node.get("is_test_data")),
        "node_id": node_id,
        "node_name": str(node.get("node_name") or "").strip(),
        "assigned_agent_id": str(node.get("assigned_agent_id") or "").strip(),
        "assigned_agent_name": str(node.get("assigned_agent_name") or "").strip(),
        "node_goal": str(node.get("node_goal") or "").strip(),
        "expected_artifact": str(node.get("expected_artifact") or "").strip(),
        "delivery_mode": str(node.get("delivery_mode") or "none").strip().lower() or "none",
        "delivery_mode_text": _delivery_mode_text(node.get("delivery_mode") or "none"),
        "delivery_receiver_agent_id": str(node.get("delivery_receiver_agent_id") or "").strip(),
        "delivery_receiver_agent_name": str(node.get("delivery_receiver_agent_name") or "").strip(),
        "artifact_delivery_status": str(node.get("artifact_delivery_status") or "pending").strip().lower() or "pending",
        "artifact_delivery_status_text": _artifact_delivery_status_text(
            node.get("artifact_delivery_status") or "pending"
        ),
        "artifact_delivered_at": str(node.get("artifact_delivered_at") or "").strip(),
        "artifact_paths": list(node.get("artifact_paths") or []),
        "status": str(node.get("status") or "").strip(),
        "status_text": str(node.get("status_text") or _node_status_text(str(node.get("status") or ""))).strip(),
        "priority": int(node.get("priority") or 0),
        "priority_label": assignment_priority_label(node.get("priority")),
        "completed_at": str(node.get("completed_at") or "").strip(),
        "success_reason": str(node.get("success_reason") or "").strip(),
        "result_ref": str(node.get("result_ref") or "").strip(),
        "failure_reason": str(node.get("failure_reason") or "").strip(),
        "created_at": str(node.get("created_at") or "").strip(),
        "updated_at": str(node.get("updated_at") or "").strip(),
        "upstream_node_ids": list(node.get("upstream_node_ids") or []),
        "downstream_node_ids": list(node.get("downstream_node_ids") or []),
        "audit_ref": _db_ref(audit_id) if audit_id else "",
    }
    if isinstance(extra, dict) and extra:
        payload["extra"] = dict(extra)
    _write_assignment_workspace_json(path, payload)
    return str(path)


def _sync_assignment_workspace_snapshot(root: Path, snapshot: dict[str, Any]) -> None:
    _persist_assignment_workspace_graph(root, snapshot=snapshot, record_state="active")
    for node in list(snapshot.get("serialized_nodes") or []):
        if isinstance(node, dict):
            _persist_assignment_workspace_node(root, node=node, record_state="active")


def _artifact_delivery_markdown(
    node: dict[str, Any],
    *,
    delivered_at: str,
    operator: str,
    artifact_label: str,
    delivery_note: str,
) -> str:
    lines = [
        f"# {artifact_label or '任务产物'}",
        "",
        f"- ticket_id: {str(node.get('ticket_id') or '').strip()}",
        f"- node_id: {str(node.get('node_id') or '').strip()}",
        f"- node_name: {str(node.get('node_name') or '').strip()}",
        f"- assigned_agent: {str(node.get('assigned_agent_name') or node.get('assigned_agent_id') or '').strip()}",
        f"- delivery_mode: {_delivery_mode_text(node.get('delivery_mode') or 'none')}",
        f"- delivery_receiver: {str(node.get('delivery_receiver_agent_name') or node.get('delivery_receiver_agent_id') or '-').strip() or '-'}",
        f"- delivered_at: {delivered_at}",
        f"- operator: {operator}",
    ]
    if str(node.get("expected_artifact") or "").strip():
        lines.append(f"- expected_artifact: {str(node.get('expected_artifact') or '').strip()}")
    if delivery_note:
        lines.extend(["", "## 交付说明", "", delivery_note])
    return "\n".join(lines).strip() + "\n"


def _artifact_paths_preview(paths: list[Any]) -> list[str]:
    preview: list[str] = []
    for raw in paths:
        text = str(raw or "").strip()
        if not text:
            continue
        preview.append(text)
    return preview


def _load_edges(conn: sqlite3.Connection, ticket_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT edge_id,from_node_id,to_node_id,edge_kind,created_at
        FROM assignment_edges
        WHERE ticket_id=?
        ORDER BY created_at ASC, edge_id ASC
        """,
        (ticket_id,),
    ).fetchall()
    return [
        {
            "edge_id": int(row["edge_id"] or 0),
            "from_node_id": str(row["from_node_id"] or "").strip(),
            "to_node_id": str(row["to_node_id"] or "").strip(),
            "edge_kind": str(row["edge_kind"] or "depends_on").strip() or "depends_on",
            "created_at": str(row["created_at"] or "").strip(),
        }
        for row in rows
    ]


def _edge_maps(edges: list[dict[str, Any]]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    upstream_map: dict[str, list[str]] = {}
    downstream_map: dict[str, list[str]] = {}
    for edge in edges:
        from_id = str(edge.get("from_node_id") or "").strip()
        to_id = str(edge.get("to_node_id") or "").strip()
        if not from_id or not to_id:
            continue
        upstream_map.setdefault(to_id, []).append(from_id)
        downstream_map.setdefault(from_id, []).append(to_id)
    return upstream_map, downstream_map


def _load_nodes(conn: sqlite3.Connection, ticket_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT
            n.node_id,n.ticket_id,n.node_name,n.assigned_agent_id,
            COALESCE(a.agent_name,n.assigned_agent_id) AS assigned_agent_name,
            n.node_goal,n.expected_artifact,n.delivery_mode,n.delivery_receiver_agent_id,
            COALESCE(r.agent_name,n.delivery_receiver_agent_id) AS delivery_receiver_agent_name,
            n.artifact_delivery_status,n.artifact_delivered_at,n.artifact_paths_json,
            n.status,n.priority,n.completed_at,
            n.success_reason,n.result_ref,n.failure_reason,n.created_at,n.updated_at
        FROM assignment_nodes n
        LEFT JOIN agent_registry a ON a.agent_id=n.assigned_agent_id
        LEFT JOIN agent_registry r ON r.agent_id=n.delivery_receiver_agent_id
        WHERE n.ticket_id=?
        ORDER BY n.created_at ASC, n.rowid ASC, n.node_id ASC
        """,
        (ticket_id,),
    ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "node_id": str(row["node_id"] or "").strip(),
                "ticket_id": str(row["ticket_id"] or "").strip(),
                "node_name": str(row["node_name"] or "").strip(),
                "assigned_agent_id": str(row["assigned_agent_id"] or "").strip(),
                "assigned_agent_name": str(row["assigned_agent_name"] or "").strip(),
                "node_goal": str(row["node_goal"] or "").strip(),
                "expected_artifact": str(row["expected_artifact"] or "").strip(),
                "delivery_mode": _normalize_delivery_mode(row["delivery_mode"] or "none"),
                "delivery_mode_text": _delivery_mode_text(row["delivery_mode"] or "none"),
                "delivery_receiver_agent_id": str(row["delivery_receiver_agent_id"] or "").strip(),
                "delivery_receiver_agent_name": str(row["delivery_receiver_agent_name"] or "").strip(),
                "artifact_delivery_status": _normalize_artifact_delivery_status(
                    row["artifact_delivery_status"] or "pending"
                ),
                "artifact_delivery_status_text": _artifact_delivery_status_text(
                    row["artifact_delivery_status"] or "pending"
                ),
                "artifact_delivered_at": str(row["artifact_delivered_at"] or "").strip(),
                "artifact_paths": list(_safe_json_list(row["artifact_paths_json"] or "[]")),
                "status": str(row["status"] or "").strip().lower(),
                "priority": int(row["priority"] or 0),
                "completed_at": str(row["completed_at"] or "").strip(),
                "success_reason": str(row["success_reason"] or "").strip(),
                "result_ref": str(row["result_ref"] or "").strip(),
                "failure_reason": str(row["failure_reason"] or "").strip(),
                "created_at": str(row["created_at"] or "").strip(),
                "updated_at": str(row["updated_at"] or "").strip(),
            }
        )
    return out


def _node_map(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(node.get("node_id") or "").strip(): dict(node)
        for node in nodes
        if str(node.get("node_id") or "").strip()
    }


def _derive_node_status(
    node_id: str,
    *,
    current_status: str,
    node_status_map: dict[str, str],
    upstream_map: dict[str, list[str]],
) -> str:
    if current_status in {"running", "succeeded", "failed"}:
        return current_status
    upstream_ids = list(upstream_map.get(node_id) or [])
    if not upstream_ids:
        return "ready"
    statuses = [str(node_status_map.get(upstream_id) or "").strip().lower() for upstream_id in upstream_ids]
    if any(status == "failed" for status in statuses):
        return "blocked"
    if all(status == "succeeded" for status in statuses):
        return "ready"
    return "pending"


def _refresh_pause_state(conn: sqlite3.Connection, ticket_id: str, now_text: str) -> None:
    row = _ensure_graph_row(conn, ticket_id)
    if str(row["scheduler_state"] or "").strip().lower() != "pause_pending":
        return
    running = int(
        (
            conn.execute(
                """
                SELECT COUNT(1) AS cnt
                FROM assignment_nodes
                WHERE ticket_id=? AND status='running'
                """,
                (ticket_id,),
            ).fetchone()
            or {"cnt": 0}
        )["cnt"]
    )
    if running > 0:
        return
    conn.execute(
        """
        UPDATE assignment_graphs
        SET scheduler_state='paused',updated_at=?
        WHERE ticket_id=?
        """,
        (now_text, ticket_id),
    )


def _refresh_all_pause_states(conn: sqlite3.Connection) -> None:
    now_text = iso_ts(now_local())
    conn.execute(
        """
        UPDATE assignment_graphs
        SET scheduler_state='paused',updated_at=?
        WHERE scheduler_state='pause_pending'
          AND ticket_id NOT IN (
              SELECT DISTINCT ticket_id
              FROM assignment_nodes
              WHERE status='running'
          )
        """,
        (now_text,),
    )


def _recompute_graph_statuses(
    conn: sqlite3.Connection,
    ticket_id: str,
    *,
    sticky_node_ids: set[str] | None = None,
) -> dict[str, str]:
    now_text = iso_ts(now_local())
    sticky = {
        str(item or "").strip()
        for item in (sticky_node_ids or set())
        if str(item or "").strip()
    }
    nodes = _load_nodes(conn, ticket_id)
    edges = _load_edges(conn, ticket_id)
    upstream_map, _downstream_map = _edge_maps(edges)
    status_map = {
        str(node["node_id"]): str(node["status"] or "").strip().lower()
        for node in nodes
    }
    for node in nodes:
        node_id = str(node["node_id"])
        if node_id in sticky:
            continue
        current_status = str(node["status"] or "").strip().lower()
        next_status = _derive_node_status(
            node_id,
            current_status=current_status,
            node_status_map=status_map,
            upstream_map=upstream_map,
        )
        if next_status == current_status:
            continue
        conn.execute(
            """
            UPDATE assignment_nodes
            SET status=?,updated_at=?
            WHERE node_id=? AND ticket_id=?
            """,
            (next_status, now_text, node_id, ticket_id),
        )
        status_map[node_id] = next_status
    _refresh_pause_state(conn, ticket_id, now_text)
    return status_map


def _graph_effective_limit(*, graph_limit: int, system_limit: int) -> int:
    if graph_limit <= 0:
        return system_limit
    return min(graph_limit, system_limit)


def _running_counts(conn: sqlite3.Connection, *, ticket_id: str) -> dict[str, int]:
    total_running = int(
        (
            conn.execute(
                "SELECT COUNT(1) AS cnt FROM assignment_nodes WHERE status='running'"
            ).fetchone()
            or {"cnt": 0}
        )["cnt"]
    )
    graph_running = int(
        (
            conn.execute(
                """
                SELECT COUNT(1) AS cnt
                FROM assignment_nodes
                WHERE ticket_id=? AND status='running'
                """,
                (ticket_id,),
            ).fetchone()
            or {"cnt": 0}
        )["cnt"]
    )
    graph_running_agents = int(
        (
            conn.execute(
                """
                SELECT COUNT(DISTINCT assigned_agent_id) AS cnt
                FROM assignment_nodes
                WHERE ticket_id=? AND status='running'
                """,
                (ticket_id,),
            ).fetchone()
            or {"cnt": 0}
        )["cnt"]
    )
    total_running_agents = int(
        (
            conn.execute(
                """
                SELECT COUNT(DISTINCT assigned_agent_id) AS cnt
                FROM assignment_nodes
                WHERE status='running'
                """
            ).fetchone()
            or {"cnt": 0}
        )["cnt"]
    )
    return {
        "system_running_node_count": total_running,
        "graph_running_node_count": graph_running,
        "running_agent_count": graph_running_agents,
        "system_running_agent_count": total_running_agents,
    }


def _node_blocking_reasons(
    node_id: str,
    *,
    node_map_by_id: dict[str, dict[str, Any]],
    upstream_map: dict[str, list[str]],
) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    for upstream_id in list(upstream_map.get(node_id) or []):
        upstream = node_map_by_id.get(upstream_id) or {}
        upstream_status = str(upstream.get("status") or "").strip().lower()
        if upstream_status == "succeeded":
            continue
        reason_code = "upstream_failed" if upstream_status == "failed" else "upstream_incomplete"
        reasons.append(
            {
                "code": reason_code,
                "node_id": upstream_id,
                "node_name": str(upstream.get("node_name") or upstream_id),
                "status": upstream_status,
                "status_text": _node_status_text(upstream_status),
            }
        )
    return reasons


def _serialize_node(
    node: dict[str, Any],
    *,
    node_map_by_id: dict[str, dict[str, Any]],
    upstream_map: dict[str, list[str]],
    downstream_map: dict[str, list[str]],
) -> dict[str, Any]:
    node_id = str(node.get("node_id") or "").strip()
    upstream_ids = list(upstream_map.get(node_id) or [])
    downstream_ids = list(downstream_map.get(node_id) or [])
    status = str(node.get("status") or "").strip().lower()
    return {
        "node_id": node_id,
        "ticket_id": str(node.get("ticket_id") or "").strip(),
        "node_name": str(node.get("node_name") or "").strip(),
        "assigned_agent_id": str(node.get("assigned_agent_id") or "").strip(),
        "assigned_agent_name": str(
            node.get("assigned_agent_name") or node.get("assigned_agent_id") or ""
        ).strip(),
        "node_goal": str(node.get("node_goal") or "").strip(),
        "expected_artifact": str(node.get("expected_artifact") or "").strip(),
        "delivery_mode": str(node.get("delivery_mode") or "none").strip().lower() or "none",
        "delivery_mode_text": _delivery_mode_text(node.get("delivery_mode") or "none"),
        "delivery_receiver_agent_id": str(node.get("delivery_receiver_agent_id") or "").strip(),
        "delivery_receiver_agent_name": str(node.get("delivery_receiver_agent_name") or "").strip(),
        "artifact_delivery_status": str(node.get("artifact_delivery_status") or "pending").strip().lower() or "pending",
        "artifact_delivery_status_text": _artifact_delivery_status_text(
            node.get("artifact_delivery_status") or "pending"
        ),
        "artifact_delivered_at": str(node.get("artifact_delivered_at") or "").strip(),
        "artifact_paths": list(node.get("artifact_paths") or []),
        "status": status,
        "status_text": _node_status_text(status),
        "priority": int(node.get("priority") or 0),
        "priority_label": assignment_priority_label(node.get("priority")),
        "completed_at": str(node.get("completed_at") or "").strip(),
        "success_reason": str(node.get("success_reason") or "").strip(),
        "result_ref": str(node.get("result_ref") or "").strip(),
        "failure_reason": str(node.get("failure_reason") or "").strip(),
        "created_at": str(node.get("created_at") or "").strip(),
        "updated_at": str(node.get("updated_at") or "").strip(),
        "upstream_node_ids": upstream_ids,
        "downstream_node_ids": downstream_ids,
        "upstream_nodes": [
            {
                "node_id": upstream_id,
                "node_name": str((node_map_by_id.get(upstream_id) or {}).get("node_name") or upstream_id),
                "status": str((node_map_by_id.get(upstream_id) or {}).get("status") or "").strip().lower(),
            }
            for upstream_id in upstream_ids
        ],
        "downstream_nodes": [
            {
                "node_id": downstream_id,
                "node_name": str((node_map_by_id.get(downstream_id) or {}).get("node_name") or downstream_id),
                "status": str((node_map_by_id.get(downstream_id) or {}).get("status") or "").strip().lower(),
            }
            for downstream_id in downstream_ids
        ],
        "blocking_reasons": _node_blocking_reasons(
            node_id,
            node_map_by_id=node_map_by_id,
            upstream_map=upstream_map,
        ),
        "last_receipt": {
            "completed_at": str(node.get("completed_at") or "").strip(),
            "success_reason": str(node.get("success_reason") or "").strip(),
            "result_ref": str(node.get("result_ref") or "").strip(),
            "failure_reason": str(node.get("failure_reason") or "").strip(),
        },
    }


def _graph_metrics(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {
        "pending": 0,
        "ready": 0,
        "running": 0,
        "succeeded": 0,
        "failed": 0,
        "blocked": 0,
    }
    for node in nodes:
        status = str(node.get("status") or "").strip().lower()
        if status in counts:
            counts[status] += 1
    return {
        "total_nodes": len(nodes),
        "status_counts": counts,
        "executed_count": counts["running"] + counts["succeeded"] + counts["failed"],
        "unexecuted_count": counts["pending"] + counts["ready"] + counts["blocked"],
    }


def _graph_overview_payload(
    graph_row: sqlite3.Row,
    *,
    metrics_summary: dict[str, Any],
    scheduler_state_payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "ticket_id": str(graph_row["ticket_id"] or "").strip(),
        "graph_name": str(graph_row["graph_name"] or "").strip(),
        "source_workflow": str(graph_row["source_workflow"] or "").strip(),
        "summary": str(graph_row["summary"] or "").strip(),
        "review_mode": str(graph_row["review_mode"] or "").strip(),
        "global_concurrency_limit": int(graph_row["global_concurrency_limit"] or 0),
        "is_test_data": _row_is_test_data(graph_row),
        "external_request_id": str(graph_row["external_request_id"] or "").strip(),
        "scheduler_state": str(graph_row["scheduler_state"] or "").strip().lower(),
        "scheduler_state_text": _scheduler_state_text(graph_row["scheduler_state"]),
        "pause_note": str(graph_row["pause_note"] or "").strip(),
        "created_at": str(graph_row["created_at"] or "").strip(),
        "updated_at": str(graph_row["updated_at"] or "").strip(),
        "metrics_summary": metrics_summary,
        "scheduler": scheduler_state_payload,
    }


def _validate_node_ids_exist(
    *,
    all_node_ids: set[str],
    upstream_node_ids: list[str],
    downstream_node_ids: list[str],
) -> None:
    missing = [
        node_id
        for node_id in list(upstream_node_ids) + list(downstream_node_ids)
        if node_id not in all_node_ids
    ]
    if missing:
        raise AssignmentCenterError(
            400,
            "dependency node not found",
            "dependency_node_not_found",
            {"missing_node_ids": missing[:20]},
        )


def _assert_no_cycles(node_ids: set[str], edges: list[tuple[str, str]]) -> None:
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    indegree: dict[str, int] = {node_id: 0 for node_id in node_ids}
    for from_id, to_id in edges:
        if from_id == to_id:
            raise AssignmentCenterError(
                400,
                "self dependency not allowed",
                "self_dependency_not_allowed",
                {"node_id": from_id},
            )
        if from_id not in adjacency or to_id not in adjacency:
            continue
        adjacency[from_id].append(to_id)
        indegree[to_id] += 1
    queue = sorted([node_id for node_id, deg in indegree.items() if deg == 0])
    visited = 0
    while queue:
        current = queue.pop(0)
        visited += 1
        for child in adjacency.get(current) or []:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
                queue.sort()
    if visited != len(node_ids):
        raise AssignmentCenterError(
            400,
            "cycle dependency detected",
            "dependency_cycle_detected",
        )


def _normalize_graph_header(conn: sqlite3.Connection, body: dict[str, Any]) -> dict[str, Any]:
    system_limit, _updated_at = _get_global_concurrency_limit(conn)
    review_mode = _normalize_review_mode(body.get("review_mode"))
    graph_name = _normalize_text(
        body.get("graph_name") or "任务中心主图",
        field="graph_name",
        required=True,
        max_len=120,
    )
    source_workflow = _normalize_text(
        body.get("source_workflow") or "workflow-ui",
        field="source_workflow",
        required=True,
        max_len=120,
    )
    summary = _normalize_text(
        body.get("summary") or "任务中心手动创建",
        field="summary",
        required=False,
        max_len=500,
    )
    external_request_id = _normalize_text(
        body.get("external_request_id") or "",
        field="external_request_id",
        required=False,
        max_len=160,
    )
    graph_limit = _normalize_positive_int(
        body.get("global_concurrency_limit"),
        field="global_concurrency_limit",
        default=system_limit,
        minimum=1,
        maximum=64,
    )
    return {
        "graph_name": graph_name,
        "source_workflow": source_workflow,
        "summary": summary,
        "review_mode": review_mode,
        "external_request_id": external_request_id,
        "global_concurrency_limit": graph_limit,
        "is_test_data": _normalize_assignment_test_flag(body.get("is_test_data"), default=False),
    }


def _resolve_assignment_agent(conn: sqlite3.Connection, cfg: Any, raw: Any) -> dict[str, str]:
    requested = _normalize_text(raw, field="assigned_agent_id", required=True, max_len=120)
    token = safe_token(requested, "", 120)
    if not token:
        raise AssignmentCenterError(400, "assigned_agent_id invalid", "assigned_agent_id_invalid")
    row = conn.execute(
        """
        SELECT agent_id,agent_name
        FROM agent_registry
        WHERE agent_id=? OR agent_name=? COLLATE NOCASE
        LIMIT 1
        """,
        (token, requested),
    ).fetchone()
    if row is not None:
        return {
            "agent_id": str(row["agent_id"] or "").strip(),
            "agent_name": str(row["agent_name"] or "").strip(),
        }
    items = []
    try:
        items = list_available_agents(cfg)
    except Exception:
        items = []
    for item in items:
        agent_name = str(item.get("agent_name") or "").strip()
        candidate_id = safe_token(agent_name, "", 120)
        if requested == agent_name or token == candidate_id:
            return {"agent_id": candidate_id, "agent_name": agent_name}
    raise AssignmentCenterError(
        400,
        "assigned_agent_id not found in training agent pool",
        "assigned_agent_not_found",
        {"assigned_agent_id": requested},
    )


def _resolve_optional_assignment_agent(conn: sqlite3.Connection, cfg: Any, raw: Any) -> dict[str, str]:
    text = str(raw or "").strip()
    if not text:
        return {"agent_id": "", "agent_name": ""}
    return _resolve_assignment_agent(conn, cfg, text)


def _normalize_dependency_lists(body: dict[str, Any]) -> tuple[list[str], list[str]]:
    upstream_raw = body.get("upstream_node_ids")
    downstream_raw = body.get("downstream_node_ids")
    if upstream_raw is None and "upstream_node_id" in body:
        upstream_raw = [body.get("upstream_node_id")]
    if downstream_raw is None and "downstream_node_id" in body:
        downstream_raw = [body.get("downstream_node_id")]
    upstream_ids = _dedupe_tokens(
        _safe_json_list(upstream_raw) if not isinstance(upstream_raw, list) else upstream_raw
    )
    downstream_ids = _dedupe_tokens(
        _safe_json_list(downstream_raw) if not isinstance(downstream_raw, list) else downstream_raw
    )
    return upstream_ids, downstream_ids


def _normalize_node_payload(
    conn: sqlite3.Connection,
    cfg: Any,
    body: dict[str, Any],
    *,
    node_id: str = "",
) -> dict[str, Any]:
    agent_meta = _resolve_assignment_agent(
        conn,
        cfg,
        body.get("assigned_agent_id") or body.get("agent_id") or body.get("agent_name"),
    )
    delivery_mode = _normalize_delivery_mode(
        body.get("delivery_mode")
        or body.get("deliveryMode")
        or body.get("artifact_delivery_mode")
        or "none"
    )
    receiver_meta = _resolve_optional_assignment_agent(
        conn,
        cfg,
        body.get("delivery_receiver_agent_id")
        or body.get("deliveryReceiverAgentId")
        or body.get("delivery_receiver_agent_name")
        or "",
    )
    if delivery_mode == "specified" and not str(receiver_meta.get("agent_id") or "").strip():
        raise AssignmentCenterError(
            400,
            "delivery_receiver_agent_id required when delivery_mode=specified",
            "delivery_receiver_agent_required",
        )
    upstream_ids, downstream_ids = _normalize_dependency_lists(body)
    node_name = _normalize_text(body.get("node_name"), field="node_name", required=True, max_len=200)
    node_goal = _normalize_text(body.get("node_goal"), field="node_goal", required=True, max_len=4000)
    expected_artifact = _normalize_text(
        body.get("expected_artifact") or "",
        field="expected_artifact",
        required=False,
        max_len=1000,
    )
    priority = normalize_assignment_priority(body.get("priority"), required=True)
    assigned_node_id = safe_token(str(body.get("node_id") or node_id or ""), "", 160) or assignment_node_id()
    return {
        "node_id": assigned_node_id,
        "node_name": node_name,
        "assigned_agent_id": str(agent_meta["agent_id"] or "").strip(),
        "assigned_agent_name": str(agent_meta["agent_name"] or "").strip(),
        "node_goal": node_goal,
        "expected_artifact": expected_artifact,
        "delivery_mode": delivery_mode,
        "delivery_receiver_agent_id": str(receiver_meta.get("agent_id") or "").strip(),
        "delivery_receiver_agent_name": str(receiver_meta.get("agent_name") or "").strip(),
        "artifact_delivery_status": "pending",
        "artifact_delivered_at": "",
        "artifact_paths": [],
        "priority": int(priority),
        "upstream_node_ids": upstream_ids,
        "downstream_node_ids": downstream_ids,
    }


def _collect_edges_from_request(
    *,
    node_payloads: list[dict[str, Any]],
    explicit_edges: list[dict[str, Any]],
) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    for node in node_payloads:
        node_id = str(node.get("node_id") or "").strip()
        for upstream_id in list(node.get("upstream_node_ids") or []):
            edges.append((str(upstream_id), node_id))
        for downstream_id in list(node.get("downstream_node_ids") or []):
            edges.append((node_id, str(downstream_id)))
    for edge in explicit_edges:
        from_id = safe_token(str(edge.get("from_node_id") or edge.get("from") or ""), "", 160)
        to_id = safe_token(str(edge.get("to_node_id") or edge.get("to") or ""), "", 160)
        if not from_id or not to_id:
            continue
        edges.append((from_id, to_id))
    deduped: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for edge in edges:
        if edge in seen:
            continue
        seen.add(edge)
        deduped.append(edge)
    return deduped


def _insert_graph_nodes(
    conn: sqlite3.Connection,
    *,
    ticket_id: str,
    node_payloads: list[dict[str, Any]],
    created_at: str,
) -> None:
    for node in node_payloads:
        node_status = _normalize_status(node.get("status") or "pending", field="status")
        node_created_at = str(node.get("created_at") or created_at).strip() or created_at
        node_updated_at = str(node.get("updated_at") or node_created_at).strip() or node_created_at
        conn.execute(
            """
            INSERT INTO assignment_nodes (
                node_id,ticket_id,node_name,assigned_agent_id,node_goal,expected_artifact,
                delivery_mode,delivery_receiver_agent_id,artifact_delivery_status,artifact_delivered_at,
                artifact_paths_json,status,priority,completed_at,success_reason,result_ref,failure_reason,created_at,updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                str(node["node_id"]),
                ticket_id,
                str(node["node_name"]),
                str(node["assigned_agent_id"]),
                str(node["node_goal"]),
                str(node["expected_artifact"]),
                str(node.get("delivery_mode") or "none"),
                str(node.get("delivery_receiver_agent_id") or ""),
                str(node.get("artifact_delivery_status") or "pending"),
                str(node.get("artifact_delivered_at") or ""),
                json.dumps(list(node.get("artifact_paths") or []), ensure_ascii=False),
                node_status,
                int(node["priority"]),
                str(node.get("completed_at") or ""),
                str(node.get("success_reason") or ""),
                str(node.get("result_ref") or ""),
                str(node.get("failure_reason") or ""),
                node_created_at,
                node_updated_at,
            ),
        )


def _insert_edges(
    conn: sqlite3.Connection,
    *,
    ticket_id: str,
    edges: list[tuple[str, str]],
    created_at: str,
) -> None:
    for from_id, to_id in edges:
        conn.execute(
            """
            INSERT OR IGNORE INTO assignment_edges (
                ticket_id,from_node_id,to_node_id,edge_kind,created_at
            ) VALUES (?,?,?,?,?)
            """,
            (ticket_id, from_id, to_id, "depends_on", created_at),
        )


def _plan_bridge_edges_after_delete(
    *,
    node_id: str,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> dict[str, Any]:
    node_order = {
        str(node.get("node_id") or "").strip(): index
        for index, node in enumerate(nodes)
        if str(node.get("node_id") or "").strip()
    }
    remaining_node_ids = {
        current_id
        for current_id in node_order
        if current_id and current_id != node_id
    }
    upstream_ids = sorted(
        {
            str(edge.get("from_node_id") or "").strip()
            for edge in edges
            if str(edge.get("to_node_id") or "").strip() == node_id
            and str(edge.get("from_node_id") or "").strip() in remaining_node_ids
        },
        key=lambda item: (node_order.get(item, 10**9), item),
    )
    downstream_ids = sorted(
        {
            str(edge.get("to_node_id") or "").strip()
            for edge in edges
            if str(edge.get("from_node_id") or "").strip() == node_id
            and str(edge.get("to_node_id") or "").strip() in remaining_node_ids
        },
        key=lambda item: (node_order.get(item, 10**9), item),
    )
    base_edges = [
        (
            str(edge.get("from_node_id") or "").strip(),
            str(edge.get("to_node_id") or "").strip(),
        )
        for edge in edges
        if str(edge.get("from_node_id") or "").strip() in remaining_node_ids
        and str(edge.get("to_node_id") or "").strip() in remaining_node_ids
        and str(edge.get("from_node_id") or "").strip() != node_id
        and str(edge.get("to_node_id") or "").strip() != node_id
    ]
    existing_edges = set(base_edges)
    bridge_added: list[dict[str, str]] = []
    bridge_skipped: list[dict[str, str]] = []
    for upstream_id in upstream_ids:
        for downstream_id in downstream_ids:
            candidate = (upstream_id, downstream_id)
            if upstream_id == downstream_id:
                bridge_skipped.append(
                    {
                        "from_node_id": upstream_id,
                        "to_node_id": downstream_id,
                        "reason": "self_loop_rejected",
                    }
                )
                continue
            if candidate in existing_edges:
                bridge_skipped.append(
                    {
                        "from_node_id": upstream_id,
                        "to_node_id": downstream_id,
                        "reason": "duplicate_edge_skipped",
                    }
                )
                continue
            try:
                _assert_no_cycles(remaining_node_ids, base_edges + [candidate])
            except AssignmentCenterError:
                bridge_skipped.append(
                    {
                        "from_node_id": upstream_id,
                        "to_node_id": downstream_id,
                        "reason": "cycle_rejected",
                    }
                )
                continue
            base_edges.append(candidate)
            existing_edges.add(candidate)
            bridge_added.append(
                {
                    "from_node_id": upstream_id,
                    "to_node_id": downstream_id,
                }
            )
    return {
        "upstream_node_ids": upstream_ids,
        "downstream_node_ids": downstream_ids,
        "bridge_added": bridge_added,
        "bridge_skipped": bridge_skipped,
    }


def _current_assignment_snapshot(conn: sqlite3.Connection, ticket_id: str) -> dict[str, Any]:
    graph_row = _ensure_graph_row(conn, ticket_id)
    nodes = _load_nodes(conn, ticket_id)
    edges = _load_edges(conn, ticket_id)
    node_map_by_id = _node_map(nodes)
    upstream_map, downstream_map = _edge_maps(edges)
    system_limit, system_limit_updated_at = _get_global_concurrency_limit(conn)
    counts = _running_counts(conn, ticket_id=ticket_id)
    scheduler_payload = {
        "state": str(graph_row["scheduler_state"] or "").strip().lower(),
        "state_text": _scheduler_state_text(graph_row["scheduler_state"]),
        "running_agent_count": int(counts["running_agent_count"]),
        "system_running_agent_count": int(counts["system_running_agent_count"]),
        "graph_running_node_count": int(counts["graph_running_node_count"]),
        "system_running_node_count": int(counts["system_running_node_count"]),
        "global_concurrency_limit": int(system_limit),
        "graph_concurrency_limit": int(graph_row["global_concurrency_limit"] or 0),
        "effective_concurrency_limit": _graph_effective_limit(
            graph_limit=int(graph_row["global_concurrency_limit"] or 0),
            system_limit=system_limit,
        ),
        "pause_note": str(graph_row["pause_note"] or "").strip(),
        "settings_updated_at": system_limit_updated_at,
    }
    serialized_nodes = [
        _serialize_node(
            node,
            node_map_by_id=node_map_by_id,
            upstream_map=upstream_map,
            downstream_map=downstream_map,
        )
        for node in nodes
    ]
    is_test_data = _row_is_test_data(graph_row)
    for node in serialized_nodes:
        node["is_test_data"] = is_test_data
    return {
        "graph_row": graph_row,
        "nodes": nodes,
        "edges": edges,
        "node_map_by_id": node_map_by_id,
        "upstream_map": upstream_map,
        "downstream_map": downstream_map,
        "metrics_summary": _graph_metrics(nodes),
        "scheduler": scheduler_payload,
        "serialized_nodes": serialized_nodes,
    }


def _normalize_history_loaded(raw: Any) -> int:
    if raw in (None, ""):
        return 0
    try:
        value = int(raw)
    except Exception:
        value = 0
    return max(0, value)


def list_assignments(root: Path, *, include_test_data: bool = True) -> dict[str, Any]:
    conn = connect_db(root)
    try:
        conn.execute("BEGIN")
        _refresh_all_pause_states(conn)
        rows = conn.execute(
            """
            SELECT
                g.ticket_id,g.graph_name,g.source_workflow,g.summary,g.review_mode,
                g.global_concurrency_limit,g.is_test_data,g.external_request_id,g.scheduler_state,g.pause_note,
                g.created_at,g.updated_at,
                COUNT(n.node_id) AS total_nodes,
                SUM(CASE WHEN n.status='running' THEN 1 ELSE 0 END) AS running_nodes,
                SUM(CASE WHEN n.status='failed' THEN 1 ELSE 0 END) AS failed_nodes,
                SUM(CASE WHEN n.status='blocked' THEN 1 ELSE 0 END) AS blocked_nodes
            FROM assignment_graphs g
            LEFT JOIN assignment_nodes n ON n.ticket_id=g.ticket_id
            WHERE (?=1 OR COALESCE(g.is_test_data,0)=0)
            GROUP BY
                g.ticket_id,g.graph_name,g.source_workflow,g.summary,g.review_mode,
                g.global_concurrency_limit,g.is_test_data,g.external_request_id,g.scheduler_state,g.pause_note,
                g.created_at,g.updated_at
            ORDER BY g.updated_at DESC, g.created_at DESC
            """
            ,
            (1 if include_test_data else 0,),
        ).fetchall()
        system_limit, system_limit_updated_at = _get_global_concurrency_limit(conn)
        conn.commit()
    finally:
        conn.close()
    items: list[dict[str, Any]] = []
    for row in rows:
        total_nodes = int(row["total_nodes"] or 0)
        items.append(
            {
                "ticket_id": str(row["ticket_id"] or "").strip(),
                "graph_name": str(row["graph_name"] or "").strip(),
                "source_workflow": str(row["source_workflow"] or "").strip(),
                "summary": str(row["summary"] or "").strip(),
                "review_mode": str(row["review_mode"] or "").strip(),
                "global_concurrency_limit": int(row["global_concurrency_limit"] or 0),
                "is_test_data": _row_is_test_data(row),
                "external_request_id": str(row["external_request_id"] or "").strip(),
                "scheduler_state": str(row["scheduler_state"] or "").strip().lower(),
                "scheduler_state_text": _scheduler_state_text(row["scheduler_state"]),
                "pause_note": str(row["pause_note"] or "").strip(),
                "created_at": str(row["created_at"] or "").strip(),
                "updated_at": str(row["updated_at"] or "").strip(),
                "metrics_summary": {
                    "total_nodes": total_nodes,
                    "running_nodes": int(row["running_nodes"] or 0),
                    "failed_nodes": int(row["failed_nodes"] or 0),
                    "blocked_nodes": int(row["blocked_nodes"] or 0),
                },
            }
        )
    return {
        "items": items,
        "settings": {
            "global_concurrency_limit": int(system_limit),
            "updated_at": system_limit_updated_at,
        },
    }


def _assignment_test_iso(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    if "T" in text:
        return text if "+" in text or text.endswith("Z") else text + "+08:00"
    return text.replace(" ", "T") + "+08:00"


def _assignment_test_graph_seed() -> tuple[list[dict[str, Any]], list[tuple[str, str]], set[str]]:
    def node(
        node_id: str,
        node_name: str,
        agent_name: str,
        *,
        goal: str,
        artifact: str,
        priority: int,
        created_at: str,
        status: str = "pending",
        completed_at: str = "",
        success_reason: str = "",
        result_ref: str = "",
        failure_reason: str = "",
        delivery_mode: str = "none",
        receiver_name: str = "",
        artifact_delivery_status: str = "pending",
        artifact_delivered_at: str = "",
    ) -> dict[str, Any]:
        completed_text = _assignment_test_iso(completed_at) if completed_at else ""
        delivered_text = _assignment_test_iso(artifact_delivered_at) if artifact_delivered_at else ""
        created_text = _assignment_test_iso(created_at)
        updated_text = delivered_text or completed_text or created_text
        return {
            "node_id": node_id,
            "node_name": node_name,
            "assigned_agent_id": agent_name,
            "assigned_agent_name": agent_name,
            "node_goal": goal,
            "expected_artifact": artifact,
            "delivery_mode": delivery_mode,
            "delivery_receiver_agent_id": receiver_name,
            "delivery_receiver_agent_name": receiver_name,
            "artifact_delivery_status": artifact_delivery_status,
            "artifact_delivered_at": delivered_text,
            "artifact_paths": [],
            "status": status,
            "priority": int(priority),
            "completed_at": completed_text,
            "success_reason": success_reason,
            "result_ref": result_ref,
            "failure_reason": failure_reason,
            "created_at": created_text,
            "updated_at": updated_text,
        }

    nodes = [
        node(
            "T1",
            "需求澄清",
            "需求分析师",
            goal="澄清输入需求、边界与依赖，形成统一开工口径。",
            artifact="澄清记录",
            priority=1,
            created_at="2026-03-14 10:00:00",
            status="succeeded",
            completed_at="2026-03-14 10:12:08",
            success_reason="运行成功",
        ),
        node(
            "T2",
            "范围收口",
            "需求分析师",
            goal="把任务中心一期边界压缩成可执行范围。",
            artifact="范围边界表",
            priority=1,
            created_at="2026-03-14 10:16:00",
            status="succeeded",
            completed_at="2026-03-14 10:24:17",
            success_reason="运行成功",
        ),
        node(
            "T3",
            "角色映射",
            "协调代理",
            goal="将任务拆分映射到执行角色与职责槽位。",
            artifact="角色映射表",
            priority=1,
            created_at="2026-03-14 10:22:00",
            status="succeeded",
            completed_at="2026-03-14 10:31:06",
            success_reason="运行成功",
        ),
        node(
            "T4",
            "基线确认",
            "需求分析师",
            goal="冻结一期基线，避免后续任务图口径漂移。",
            artifact="基线快照",
            priority=1,
            created_at="2026-03-14 10:34:00",
            status="succeeded",
            completed_at="2026-03-14 10:46:11",
            success_reason="运行成功",
        ),
        node(
            "T5",
            "数据备份",
            "协调代理",
            goal="在变更前完成运行态与产物目录备份。",
            artifact="备份结果",
            priority=1,
            created_at="2026-03-14 11:02:00",
            status="succeeded",
            completed_at="2026-03-14 11:18:09",
            success_reason="运行成功",
        ),
        node(
            "T6",
            "任务拆分",
            "需求分析师",
            goal="输出任务树并明确上下游依赖。",
            artifact="任务树",
            priority=1,
            created_at="2026-03-14 11:22:00",
            status="succeeded",
            completed_at="2026-03-14 11:31:25",
            success_reason="运行成功",
        ),
        node(
            "T7",
            "原型骨架",
            "设计代理",
            goal="搭建任务中心界面结构和交互骨架。",
            artifact="低保真原型",
            priority=1,
            created_at="2026-03-14 11:28:00",
            status="succeeded",
            completed_at="2026-03-14 11:44:40",
            success_reason="运行成功",
        ),
        node(
            "T8",
            "节点映射",
            "协调代理",
            goal="把任务树映射为可视化依赖图节点与连线。",
            artifact="依赖关系图",
            priority=1,
            created_at="2026-03-14 11:48:00",
            status="succeeded",
            completed_at="2026-03-14 12:01:18",
            success_reason="运行成功",
            artifact_delivery_status="delivered",
            artifact_delivered_at="2026-03-14 12:02:07",
        ),
        node(
            "T16",
            "知识快照",
            "知识代理",
            goal="固化当前知识面和原型决策快照。",
            artifact="快照归档",
            priority=2,
            created_at="2026-03-14 12:04:00",
            status="succeeded",
            completed_at="2026-03-14 12:08:56",
            success_reason="运行成功",
        ),
        node(
            "T9",
            "接口预留",
            "后端代理",
            goal="补齐任务中心所需接口字段与返回结构。",
            artifact="接口草案",
            priority=0,
            created_at="2026-03-14 12:09:20",
            status="running",
            delivery_mode="specified",
            receiver_name="测试代理",
        ),
        node(
            "T20",
            "沙箱试跑",
            "执行代理",
            goal="在沙箱环境验证调度与交付链路。",
            artifact="失败日志",
            priority=0,
            created_at="2026-03-14 12:14:00",
            status="failed",
            completed_at="2026-03-14 12:19:33",
            failure_reason="运行失败：沙箱冒烟未通过。",
        ),
        node(
            "T10",
            "联调验收",
            "测试代理",
            goal="等待接口和试跑结果后完成联调验收。",
            artifact="待补充联调记录",
            priority=0,
            created_at="2026-03-14 12:20:00",
            status="blocked",
            delivery_mode="specified",
            receiver_name="测试代理",
        ),
        node(
            "T11",
            "回写关闭",
            "协调代理",
            goal="回写执行结果并推动关闭流程。",
            artifact="关闭回写单",
            priority=1,
            created_at="2026-03-14 12:22:00",
        ),
        node(
            "T12",
            "回执汇总",
            "分析代理",
            goal="汇总各节点回执结果与差异。",
            artifact="回执汇总",
            priority=1,
            created_at="2026-03-14 12:26:00",
        ),
        node(
            "T13",
            "结果广播",
            "协调代理",
            goal="向上下游广播本轮执行结果。",
            artifact="广播记录",
            priority=1,
            created_at="2026-03-14 12:28:00",
        ),
        node(
            "T17",
            "风险巡检",
            "风险代理",
            goal="抽检独立风险项，验证任务图边界稳定性。",
            artifact="风险巡检单",
            priority=2,
            created_at="2026-03-14 12:30:00",
        ),
        node(
            "T14",
            "人工确认",
            "人工审核",
            goal="在结果广播后执行人工确认。",
            artifact="人工确认结论",
            priority=1,
            created_at="2026-03-14 12:32:00",
        ),
        node(
            "T15",
            "自动关闭",
            "协调代理",
            goal="满足关闭条件后自动完成收口。",
            artifact="关闭结果",
            priority=1,
            created_at="2026-03-14 12:36:00",
        ),
        node(
            "T18",
            "模板同步",
            "知识代理",
            goal="同步原型模板与任务中心最新约束。",
            artifact="模板同步记录",
            priority=2,
            created_at="2026-03-14 12:40:00",
        ),
        node(
            "T19",
            "资源回收",
            "运维代理",
            goal="在主链完成后执行资源回收。",
            artifact="资源回收单",
            priority=2,
            created_at="2026-03-14 12:42:00",
        ),
    ]
    edges = [
        ("T1", "T2"),
        ("T1", "T3"),
        ("T2", "T4"),
        ("T3", "T4"),
        ("T4", "T5"),
        ("T5", "T6"),
        ("T5", "T7"),
        ("T6", "T8"),
        ("T7", "T8"),
        ("T8", "T9"),
        ("T9", "T10"),
        ("T20", "T10"),
        ("T10", "T11"),
        ("T11", "T12"),
        ("T11", "T13"),
        ("T12", "T15"),
        ("T13", "T14"),
        ("T14", "T15"),
    ]
    return nodes, edges, {"T17", "T18", "T19"}


def bootstrap_assignment_test_graph(cfg: Any, *, operator: str) -> dict[str, Any]:
    operator_text = _default_assignment_operator(operator)
    seed_nodes, seed_edges, sticky_node_ids = _assignment_test_graph_seed()
    conn = connect_db(cfg.root)
    created = False
    seeded = False
    ticket_id = ""
    bootstrap_updated_at = iso_ts(now_local())
    try:
        conn.execute("BEGIN IMMEDIATE")
        graph_row = conn.execute(
            """
            SELECT
                ticket_id,graph_name,source_workflow,summary,review_mode,
                global_concurrency_limit,is_test_data,external_request_id,scheduler_state,pause_note,
                created_at,updated_at
            FROM assignment_graphs
            WHERE source_workflow=? AND external_request_id=?
            LIMIT 1
            """,
            (ASSIGNMENT_TEST_GRAPH_SOURCE, ASSIGNMENT_TEST_GRAPH_EXTERNAL_REQUEST_ID),
        ).fetchone()
        if graph_row is None:
            ticket_id = assignment_ticket_id()
            conn.execute(
                """
                INSERT INTO assignment_graphs (
                    ticket_id,graph_name,source_workflow,summary,review_mode,
                    global_concurrency_limit,is_test_data,external_request_id,scheduler_state,pause_note,created_at,updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    ticket_id,
                    ASSIGNMENT_TEST_GRAPH_NAME,
                    ASSIGNMENT_TEST_GRAPH_SOURCE,
                    ASSIGNMENT_TEST_GRAPH_SUMMARY,
                    "none",
                    DEFAULT_ASSIGNMENT_CONCURRENCY_LIMIT,
                    1,
                    ASSIGNMENT_TEST_GRAPH_EXTERNAL_REQUEST_ID,
                    "running",
                    "",
                    ASSIGNMENT_TEST_GRAPH_CREATED_AT,
                    bootstrap_updated_at,
                ),
            )
            created = True
        else:
            ticket_id = str(graph_row["ticket_id"] or "").strip()
            conn.execute(
                """
                UPDATE assignment_graphs
                SET graph_name=?,summary=?,review_mode='none',
                    global_concurrency_limit=?,is_test_data=1,
                    external_request_id=?,updated_at=?
                WHERE ticket_id=?
                """,
                (
                    ASSIGNMENT_TEST_GRAPH_NAME,
                    ASSIGNMENT_TEST_GRAPH_SUMMARY,
                    DEFAULT_ASSIGNMENT_CONCURRENCY_LIMIT,
                    ASSIGNMENT_TEST_GRAPH_EXTERNAL_REQUEST_ID,
                    bootstrap_updated_at,
                    ticket_id,
                ),
            )
        existing_node_count = int(
            (
                conn.execute(
                    "SELECT COUNT(1) AS cnt FROM assignment_nodes WHERE ticket_id=?",
                    (ticket_id,),
                ).fetchone()
                or {"cnt": 0}
            )["cnt"]
        )
        if existing_node_count <= 0:
            seeded = True
            conn.execute("DELETE FROM assignment_edges WHERE ticket_id=?", (ticket_id,))
            conn.execute("DELETE FROM assignment_nodes WHERE ticket_id=?", (ticket_id,))
            _insert_graph_nodes(
                conn,
                ticket_id=ticket_id,
                node_payloads=seed_nodes,
                created_at=ASSIGNMENT_TEST_GRAPH_CREATED_AT,
            )
            _insert_edges(
                conn,
                ticket_id=ticket_id,
                edges=seed_edges,
                created_at=ASSIGNMENT_TEST_GRAPH_CREATED_AT,
            )
            _recompute_graph_statuses(conn, ticket_id, sticky_node_ids=sticky_node_ids)
            snapshot_seed = _current_assignment_snapshot(conn, ticket_id)
            node_map_seed = snapshot_seed["node_map_by_id"]
            delivered_node = node_map_seed.get("T8") or {}
            if delivered_node:
                delivered_paths = [path.as_posix() for path in _node_artifact_file_paths(cfg.root, delivered_node)]
                delivered_payload = _artifact_delivery_markdown(
                    delivered_node,
                    delivered_at=_assignment_test_iso("2026-03-14 12:02:07"),
                    operator=operator_text,
                    artifact_label=str(
                        delivered_node.get("expected_artifact") or delivered_node.get("node_name") or "依赖关系图"
                    ),
                    delivery_note="任务中心原型测试数据预置交付产物。",
                )
                for raw_path in delivered_paths:
                    path = Path(raw_path).resolve(strict=False)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(delivered_payload, encoding="utf-8")
                result_ref = delivered_paths[0] if delivered_paths else ""
                conn.execute(
                    """
                    UPDATE assignment_nodes
                    SET artifact_delivery_status='delivered',
                        artifact_delivered_at=?,
                        artifact_paths_json=?,
                        result_ref=?,
                        updated_at=?
                    WHERE ticket_id=? AND node_id='T8'
                    """,
                    (
                        _assignment_test_iso("2026-03-14 12:02:07"),
                        json.dumps(delivered_paths, ensure_ascii=False),
                        result_ref,
                        _assignment_test_iso("2026-03-14 12:02:07"),
                        ticket_id,
                    ),
                )
            failed_node = node_map_seed.get("T20") or {}
            if failed_node:
                failed_paths = [path.as_posix() for path in _node_artifact_file_paths(cfg.root, failed_node)]
                failed_payload = "\n".join(
                    [
                        "# 沙箱试跑失败日志",
                        "",
                        "- node_id: T20",
                        "- node_name: 沙箱试跑",
                        "- completed_at: 2026-03-14T12:19:33+08:00",
                        "- failure_reason: 运行失败：沙箱冒烟未通过。",
                        "",
                        "## 摘要",
                        "",
                        "接口联调前置检查未通过，调度链路保持阻塞。",
                        "",
                    ]
                )
                for raw_path in failed_paths:
                    path = Path(raw_path).resolve(strict=False)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(failed_payload, encoding="utf-8")
                conn.execute(
                    """
                    UPDATE assignment_nodes
                    SET artifact_paths_json=?,updated_at=?
                    WHERE ticket_id=? AND node_id='T20'
                    """,
                    (
                        json.dumps(failed_paths, ensure_ascii=False),
                        _assignment_test_iso("2026-03-14 12:19:33"),
                        ticket_id,
                    ),
                )
            conn.execute(
                """
                UPDATE assignment_graphs
                SET scheduler_state='running',pause_note='',updated_at=?
                WHERE ticket_id=?
                """,
                (bootstrap_updated_at, ticket_id),
            )
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    _sync_assignment_workspace_snapshot(cfg.root, snapshot)
    return {
        "ticket_id": ticket_id,
        "created": bool(created or seeded),
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
    }


def create_assignment_graph(cfg: Any, body: dict[str, Any]) -> dict[str, Any]:
    operator = _default_assignment_operator(body.get("operator"))
    now_text = iso_ts(now_local())
    explicit_nodes = body.get("nodes")
    explicit_edges = body.get("edges")
    raw_nodes = explicit_nodes if isinstance(explicit_nodes, list) else []
    raw_edges = explicit_edges if isinstance(explicit_edges, list) else []
    conn = connect_db(cfg.root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        graph_payload = _normalize_graph_header(conn, body)
        external_request_id = str(graph_payload["external_request_id"] or "").strip()
        if external_request_id:
            existed = conn.execute(
                """
                SELECT ticket_id
                FROM assignment_graphs
                WHERE source_workflow=? AND external_request_id=?
                LIMIT 1
                """,
                (str(graph_payload["source_workflow"]), external_request_id),
            ).fetchone()
            if existed is not None:
                ticket_id = str(existed["ticket_id"] or "").strip()
                snapshot = _current_assignment_snapshot(conn, ticket_id)
                conn.commit()
                return {
                    "ticket_id": ticket_id,
                    "created": False,
                    "graph_overview": _graph_overview_payload(
                        snapshot["graph_row"],
                        metrics_summary=snapshot["metrics_summary"],
                        scheduler_state_payload=snapshot["scheduler"],
                    ),
                }
        ticket_id = assignment_ticket_id()
        node_payloads = [
            _normalize_node_payload(conn, cfg, raw if isinstance(raw, dict) else {}, node_id="")
            for raw in raw_nodes
        ]
        requested_node_ids = {str(node["node_id"]) for node in node_payloads}
        if len(requested_node_ids) != len(node_payloads):
            raise AssignmentCenterError(400, "node_id duplicated", "node_id_duplicated")
        collected_edges = _collect_edges_from_request(
            node_payloads=node_payloads,
            explicit_edges=[raw for raw in raw_edges if isinstance(raw, dict)],
        )
        _assert_no_cycles(requested_node_ids, collected_edges)
        _validate_node_ids_exist(
            all_node_ids=requested_node_ids,
            upstream_node_ids=[from_id for from_id, _to_id in collected_edges],
            downstream_node_ids=[to_id for _from_id, to_id in collected_edges],
        )
        conn.execute(
            """
            INSERT INTO assignment_graphs (
                ticket_id,graph_name,source_workflow,summary,review_mode,
                global_concurrency_limit,is_test_data,external_request_id,scheduler_state,pause_note,created_at,updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                ticket_id,
                str(graph_payload["graph_name"]),
                str(graph_payload["source_workflow"]),
                str(graph_payload["summary"]),
                str(graph_payload["review_mode"]),
                int(graph_payload["global_concurrency_limit"]),
                1 if graph_payload.get("is_test_data") else 0,
                external_request_id,
                "idle",
                "",
                now_text,
                now_text,
            ),
        )
        _insert_graph_nodes(conn, ticket_id=ticket_id, node_payloads=node_payloads, created_at=now_text)
        _insert_edges(conn, ticket_id=ticket_id, edges=collected_edges, created_at=now_text)
        _recompute_graph_statuses(conn, ticket_id)
        audit_id = _write_assignment_audit(
            conn,
            ticket_id=ticket_id,
            node_id="",
            action="create_graph",
            operator=operator,
            reason="create assignment graph",
            target_status="idle",
            detail={
                "graph_name": graph_payload["graph_name"],
                "source_workflow": graph_payload["source_workflow"],
                "node_count": len(node_payloads),
                "edge_count": len(collected_edges),
                "review_mode": graph_payload["review_mode"],
                "global_concurrency_limit": graph_payload["global_concurrency_limit"],
                "is_test_data": bool(graph_payload.get("is_test_data")),
                "external_request_id": external_request_id,
                "workspace_root": str(_assignment_workspace_root(cfg.root)),
            },
            created_at=now_text,
        )
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    _sync_assignment_workspace_snapshot(cfg.root, snapshot)
    return {
        "ticket_id": ticket_id,
        "created": True,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
        "created_node_ids": [str(node["node_id"]) for node in node_payloads],
        "created_edge_count": len(collected_edges),
        "audit_id": audit_id,
    }


def get_assignment_overview(root: Path, ticket_id_text: str, *, include_test_data: bool = True) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    if not ticket_id:
        raise AssignmentCenterError(400, "ticket_id required", "ticket_id_required")
    conn = connect_db(root)
    try:
        conn.execute("BEGIN")
        _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
        _refresh_pause_state(conn, ticket_id, iso_ts(now_local()))
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    return {
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
        "priority_rules": {
            "ui_levels": ["P0", "P1", "P2", "P3"],
            "backend_levels": [0, 1, 2, 3],
            "highest_first": True,
            "tie_breaker": "created_at_asc",
        },
    }


def get_assignment_graph(
    root: Path,
    ticket_id_text: str,
    *,
    history_loaded: Any = 0,
    history_batch_size: Any = 12,
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    if not ticket_id:
        raise AssignmentCenterError(400, "ticket_id required", "ticket_id_required")
    extra_loaded = _normalize_history_loaded(history_loaded)
    batch_size = _normalize_positive_int(
        history_batch_size,
        field="history_batch_size",
        default=12,
        minimum=1,
        maximum=50,
    )
    base_recent = 12
    conn = connect_db(root)
    try:
        conn.execute("BEGIN")
        _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
        _refresh_pause_state(conn, ticket_id, iso_ts(now_local()))
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    nodes = list(snapshot["serialized_nodes"])
    completed_nodes = [
        node
        for node in nodes
        if str(node.get("status") or "").strip().lower() in {"succeeded", "failed"}
    ]
    completed_nodes.sort(
        key=lambda item: (
            str(item.get("completed_at") or ""),
            str(item.get("created_at") or ""),
            str(item.get("node_id") or ""),
        ),
        reverse=True,
    )
    non_completed_nodes = [
        node
        for node in nodes
        if str(node.get("status") or "").strip().lower() not in {"succeeded", "failed"}
    ]
    visible_completed = completed_nodes[: min(len(completed_nodes), base_recent + extra_loaded)]
    visible_ids = {
        str(node.get("node_id") or "").strip()
        for node in non_completed_nodes + visible_completed
        if str(node.get("node_id") or "").strip()
    }
    visible_edges = [
        edge
        for edge in snapshot["edges"]
        if str(edge.get("from_node_id") or "").strip() in visible_ids
        and str(edge.get("to_node_id") or "").strip() in visible_ids
    ]
    remaining = max(0, len(completed_nodes) - len(visible_completed))
    visible_nodes = non_completed_nodes + visible_completed
    visible_nodes.sort(
        key=lambda item: (
            0
            if str(item.get("status") or "").strip().lower() in {"running", "succeeded", "failed"}
            else 1,
            int(item.get("priority") or 0),
            str(item.get("completed_at") or ""),
            str(item.get("created_at") or ""),
            str(item.get("node_id") or ""),
        )
    )
    return {
        "ticket_id": ticket_id,
        "graph": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
        "nodes": visible_nodes,
        "edges": visible_edges,
        "node_catalog": [
            {
                "node_id": str(node.get("node_id") or "").strip(),
                "node_name": str(node.get("node_name") or "").strip(),
                "status": str(node.get("status") or "").strip().lower(),
                "priority": int(node.get("priority") or 0),
                "priority_label": assignment_priority_label(node.get("priority")),
            }
            for node in nodes
        ],
        "metrics_summary": snapshot["metrics_summary"],
        "priority_rules": {
            "ui_levels": ["P0", "P1", "P2", "P3"],
            "backend_levels": [0, 1, 2, 3],
            "highest_first": True,
            "tie_breaker": "created_at_asc",
        },
        "history": {
            "base_recent_count": min(base_recent, len(completed_nodes)),
            "loaded_extra_count": max(0, len(visible_completed) - min(base_recent, len(completed_nodes))),
            "next_history_loaded": extra_loaded + batch_size,
            "remaining_completed_count": remaining,
            "has_more": remaining > 0,
            "batch_size": batch_size,
        },
    }


def get_assignment_scheduler_state(root: Path, ticket_id_text: str, *, include_test_data: bool = True) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    if not ticket_id:
        raise AssignmentCenterError(400, "ticket_id required", "ticket_id_required")
    conn = connect_db(root)
    try:
        conn.execute("BEGIN")
        graph_row = _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
        _refresh_pause_state(conn, ticket_id, iso_ts(now_local()))
        graph_row = _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
        system_limit, settings_updated_at = _get_global_concurrency_limit(conn)
        counts = _running_counts(conn, ticket_id=ticket_id)
        conn.commit()
    finally:
        conn.close()
    graph_limit = int(graph_row["global_concurrency_limit"] or 0)
    return {
        "ticket_id": ticket_id,
        "state": str(graph_row["scheduler_state"] or "").strip().lower(),
        "state_text": _scheduler_state_text(graph_row["scheduler_state"]),
        "running_agent_count": int(counts["running_agent_count"]),
        "system_running_agent_count": int(counts["system_running_agent_count"]),
        "graph_running_node_count": int(counts["graph_running_node_count"]),
        "system_running_node_count": int(counts["system_running_node_count"]),
        "global_concurrency_limit": int(system_limit),
        "graph_concurrency_limit": graph_limit,
        "effective_concurrency_limit": _graph_effective_limit(
            graph_limit=graph_limit,
            system_limit=system_limit,
        ),
        "pause_note": str(graph_row["pause_note"] or "").strip(),
        "settings_updated_at": settings_updated_at,
    }


def get_assignment_status_detail(
    root: Path,
    ticket_id_text: str,
    *,
    node_id_text: str = "",
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    node_id = safe_token(str(node_id_text or ""), "", 160)
    if not ticket_id:
        raise AssignmentCenterError(400, "ticket_id required", "ticket_id_required")
    conn = connect_db(root)
    try:
        conn.execute("BEGIN")
        _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
        _refresh_pause_state(conn, ticket_id, iso_ts(now_local()))
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        if not snapshot["nodes"]:
            selected_node = {}
        else:
            selected_node = snapshot["node_map_by_id"].get(node_id) or (snapshot["nodes"][0] if snapshot["nodes"] else {})
        audit_rows = conn.execute(
            """
            SELECT audit_id,action,operator,reason,target_status,ref,created_at,detail_json
            FROM assignment_audit_log
            WHERE ticket_id=?
              AND (?='' OR node_id=? OR COALESCE(node_id,'')='')
            ORDER BY created_at DESC, audit_id DESC
            LIMIT 12
            """,
            (ticket_id, node_id, node_id),
        ).fetchall()
        conn.commit()
    finally:
        conn.close()
    selected_serialized = (
        _serialize_node(
            selected_node,
            node_map_by_id=snapshot["node_map_by_id"],
            upstream_map=snapshot["upstream_map"],
            downstream_map=snapshot["downstream_map"],
        )
        if selected_node
        else {}
    )
    selected_status = str(selected_serialized.get("status") or "").strip().lower()
    available_actions: list[str] = []
    if selected_status == "running":
        available_actions.extend(["mark-success", "mark-failed"])
    if selected_status == "failed":
        available_actions.extend(["rerun", "override-status"])
    if selected_status:
        available_actions.append("deliver-artifact")
    if list(selected_serialized.get("artifact_paths") or []):
        available_actions.append("view-artifact")
    if selected_status and selected_status != "running":
        available_actions.append("delete")
    audit_refs = []
    for row in audit_rows:
        detail = _json_load(row["detail_json"], {})
        if not isinstance(detail, dict):
            detail = {}
        audit_refs.append(
            {
                "audit_id": str(row["audit_id"] or "").strip(),
                "action": str(row["action"] or "").strip(),
                "operator": str(row["operator"] or "").strip(),
                "reason": str(row["reason"] or "").strip(),
                "target_status": str(row["target_status"] or "").strip(),
                "ref": str(row["ref"] or "").strip(),
                "created_at": str(row["created_at"] or "").strip(),
                "detail": detail,
            }
        )
    return {
        "ticket_id": ticket_id,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
        "selected_node": selected_serialized,
        "blocking_reasons": list(selected_serialized.get("blocking_reasons") or []),
        "available_actions": available_actions,
        "audit_refs": audit_refs,
    }


def deliver_assignment_artifact(
    root: Path,
    *,
    ticket_id_text: str,
    node_id_text: str,
    operator: str,
    artifact_label: Any = "",
    delivery_note: Any = "",
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    node_id = safe_token(str(node_id_text or ""), "", 160)
    if not ticket_id or not node_id:
        raise AssignmentCenterError(400, "ticket_id/node_id required", "ticket_or_node_required")
    operator_text = _default_assignment_operator(operator)
    label_text = _normalize_text(artifact_label, field="artifact_label", required=False, max_len=200)
    note_text = _normalize_text(delivery_note, field="delivery_note", required=False, max_len=4000)
    now_text = iso_ts(now_local())
    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_ticket_node_row_visible(conn, ticket_id, node_id, include_test_data=include_test_data)
        snapshot_before = _current_assignment_snapshot(conn, ticket_id)
        selected_node = snapshot_before["node_map_by_id"].get(node_id) or {}
        if not selected_node:
            raise AssignmentCenterError(404, "assignment node not found", "assignment_node_not_found")
        artifact_file_paths = _node_artifact_file_paths(root, selected_node)
        artifact_paths: list[str] = []
        artifact_name = label_text or (
            str(selected_node.get("expected_artifact") or "").strip()
            or str(selected_node.get("node_name") or "").strip()
            or str(selected_node.get("node_id") or "").strip()
            or "任务产物"
        )
        payload = _artifact_delivery_markdown(
            selected_node,
            delivered_at=now_text,
            operator=operator_text,
            artifact_label=artifact_name,
            delivery_note=note_text,
        )
        for path in artifact_file_paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(payload, encoding="utf-8")
            artifact_paths.append(path.as_posix())
        conn.execute(
            """
            UPDATE assignment_nodes
            SET artifact_delivery_status='delivered',
                artifact_delivered_at=?,
                artifact_paths_json=?,
                updated_at=?
            WHERE ticket_id=? AND node_id=?
            """,
            (
                now_text,
                json.dumps(artifact_paths, ensure_ascii=False),
                now_text,
                ticket_id,
                node_id,
            ),
        )
        audit_id = _write_assignment_audit(
            conn,
            ticket_id=ticket_id,
            node_id=node_id,
            action="deliver_artifact",
            operator=operator_text,
            reason=note_text or "deliver assignment artifact",
            target_status="delivered",
            detail={
                "artifact_label": artifact_name,
                "delivery_mode": str(selected_node.get("delivery_mode") or "none").strip().lower(),
                "delivery_receiver_agent_id": str(selected_node.get("delivery_receiver_agent_id") or "").strip(),
                "artifact_paths": artifact_paths,
            },
            created_at=now_text,
        )
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    _sync_assignment_workspace_snapshot(root, snapshot)
    delivered_node = next(
        (node for node in snapshot["serialized_nodes"] if str(node.get("node_id") or "").strip() == node_id),
        {},
    )
    return {
        "ticket_id": ticket_id,
        "node": delivered_node,
        "artifact_paths": artifact_paths,
        "audit_id": audit_id,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
    }


def read_assignment_artifact_preview(
    root: Path,
    *,
    ticket_id_text: str,
    node_id_text: str,
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    node_id = safe_token(str(node_id_text or ""), "", 160)
    if not ticket_id or not node_id:
        raise AssignmentCenterError(400, "ticket_id/node_id required", "ticket_or_node_required")
    conn = connect_db(root)
    try:
        conn.execute("BEGIN")
        _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    selected_node = snapshot["node_map_by_id"].get(node_id) or {}
    if not selected_node:
        raise AssignmentCenterError(404, "assignment node not found", "assignment_node_not_found")
    artifact_paths = list(selected_node.get("artifact_paths") or [])
    if not artifact_paths:
        raise AssignmentCenterError(404, "artifact not delivered", "artifact_not_delivered")
    artifact_root = _assignment_artifact_root(root)
    path = Path(str(artifact_paths[0])).resolve(strict=False)
    if not path_in_scope(path, artifact_root):
        raise AssignmentCenterError(400, "artifact path out of root", "artifact_path_out_of_root")
    if not path.exists() or not path.is_file():
        raise AssignmentCenterError(404, "artifact file missing", "artifact_file_missing")
    return {
        "ticket_id": ticket_id,
        "node_id": node_id,
        "path": path.as_posix(),
        "content": path.read_text(encoding="utf-8"),
        "content_type": "text/plain; charset=utf-8",
    }


def create_assignment_node(
    cfg: Any,
    ticket_id_text: str,
    body: dict[str, Any],
    *,
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    if not ticket_id:
        raise AssignmentCenterError(400, "ticket_id required", "ticket_id_required")
    operator = _default_assignment_operator(body.get("operator"))
    now_text = iso_ts(now_local())
    conn = connect_db(cfg.root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
        node_payload = _normalize_node_payload(conn, cfg, body, node_id="")
        existing_nodes = _load_nodes(conn, ticket_id)
        existing_node_ids = {str(node["node_id"]) for node in existing_nodes}
        if str(node_payload["node_id"]) in existing_node_ids:
            raise AssignmentCenterError(409, "node_id duplicated", "node_id_duplicated")
        _validate_node_ids_exist(
            all_node_ids=existing_node_ids,
            upstream_node_ids=list(node_payload["upstream_node_ids"]),
            downstream_node_ids=list(node_payload["downstream_node_ids"]),
        )
        existing_edges = [
            (
                str(edge.get("from_node_id") or "").strip(),
                str(edge.get("to_node_id") or "").strip(),
            )
            for edge in _load_edges(conn, ticket_id)
        ]
        new_edges = _collect_edges_from_request(node_payloads=[node_payload], explicit_edges=[])
        _assert_no_cycles(existing_node_ids | {str(node_payload["node_id"])}, existing_edges + new_edges)
        _insert_graph_nodes(conn, ticket_id=ticket_id, node_payloads=[node_payload], created_at=now_text)
        _insert_edges(conn, ticket_id=ticket_id, edges=new_edges, created_at=now_text)
        _recompute_graph_statuses(conn, ticket_id)
        audit_id = _write_assignment_audit(
            conn,
            ticket_id=ticket_id,
            node_id=str(node_payload["node_id"]),
            action="create_node",
            operator=operator,
            reason="create assignment node",
            target_status="pending",
            detail={
                "node_name": node_payload["node_name"],
                "assigned_agent_id": node_payload["assigned_agent_id"],
                "priority": int(node_payload["priority"]),
                "priority_label": assignment_priority_label(node_payload["priority"]),
                "upstream_node_ids": list(node_payload["upstream_node_ids"]),
                "downstream_node_ids": list(node_payload["downstream_node_ids"]),
                "expected_artifact": node_payload["expected_artifact"],
                "delivery_mode": node_payload["delivery_mode"],
                "delivery_receiver_agent_id": node_payload["delivery_receiver_agent_id"],
                "workspace_root": str(_assignment_workspace_root(cfg.root)),
            },
            created_at=now_text,
        )
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    _sync_assignment_workspace_snapshot(cfg.root, snapshot)
    created_node = next(
        (
            node
            for node in snapshot["serialized_nodes"]
            if str(node.get("node_id") or "").strip() == str(node_payload["node_id"])
        ),
        {},
    )
    return {
        "ticket_id": ticket_id,
        "node": created_node,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
        "audit_id": audit_id,
    }


def _ready_dispatch_candidates(conn: sqlite3.Connection, *, ticket_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT node_id,node_name,assigned_agent_id,status,priority,created_at,updated_at
        FROM assignment_nodes
        WHERE ticket_id=? AND status='ready'
        ORDER BY priority ASC, created_at ASC, node_id ASC
        """,
        (ticket_id,),
    ).fetchall()
    return [_row_dict(row) for row in rows]


def dispatch_assignment_next(
    root: Path,
    *,
    ticket_id_text: str,
    operator: str,
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    if not ticket_id:
        raise AssignmentCenterError(400, "ticket_id required", "ticket_id_required")
    operator_text = _default_assignment_operator(operator)
    now_text = iso_ts(now_local())
    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        graph_row = _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
        _recompute_graph_statuses(conn, ticket_id)
        graph_row = _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
        scheduler_state = str(graph_row["scheduler_state"] or "").strip().lower()
        if scheduler_state != "running":
            snapshot = _current_assignment_snapshot(conn, ticket_id)
            conn.commit()
            return {
                "ticket_id": ticket_id,
                "dispatched": [],
                "skipped": [],
                "message": "scheduler_not_running",
                "graph_overview": _graph_overview_payload(
                    snapshot["graph_row"],
                    metrics_summary=snapshot["metrics_summary"],
                    scheduler_state_payload=snapshot["scheduler"],
                ),
            }
        system_limit, _updated_at = _get_global_concurrency_limit(conn)
        counts = _running_counts(conn, ticket_id=ticket_id)
        graph_limit = int(graph_row["global_concurrency_limit"] or 0)
        effective_limit = _graph_effective_limit(graph_limit=graph_limit, system_limit=system_limit)
        graph_slots = max(0, effective_limit - int(counts["graph_running_node_count"]))
        system_slots = max(0, system_limit - int(counts["system_running_node_count"]))
        dispatch_slots = min(graph_slots, system_slots)
        dispatched: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        running_agents = {
            str(row["assigned_agent_id"] or "").strip()
            for row in conn.execute(
                "SELECT assigned_agent_id FROM assignment_nodes WHERE status='running'"
            ).fetchall()
            if str(row["assigned_agent_id"] or "").strip()
        }
        if dispatch_slots <= 0:
            snapshot = _current_assignment_snapshot(conn, ticket_id)
            conn.commit()
            return {
                "ticket_id": ticket_id,
                "dispatched": [],
                "skipped": [
                    {
                        "code": "concurrency_limit_reached",
                        "message": "global_or_graph_concurrency_limit_reached",
                    }
                ],
                "graph_overview": _graph_overview_payload(
                    snapshot["graph_row"],
                    metrics_summary=snapshot["metrics_summary"],
                    scheduler_state_payload=snapshot["scheduler"],
                ),
            }
        candidates = _ready_dispatch_candidates(conn, ticket_id=ticket_id)
        for candidate in candidates:
            if dispatch_slots <= 0:
                break
            node_id = str(candidate.get("node_id") or "").strip()
            agent_id = str(candidate.get("assigned_agent_id") or "").strip()
            if not node_id or not agent_id:
                continue
            if agent_id in running_agents:
                skipped.append(
                    {
                        "node_id": node_id,
                        "code": "agent_busy",
                        "message": "assigned agent already has running node",
                    }
                )
                continue
            before_changes = conn.total_changes
            conn.execute(
                """
                UPDATE assignment_nodes
                SET status='running',updated_at=?
                WHERE ticket_id=? AND node_id=? AND status='ready'
                """,
                (now_text, ticket_id, node_id),
            )
            if conn.total_changes <= before_changes:
                continue
            running_agents.add(agent_id)
            dispatch_slots -= 1
            audit_id = _write_assignment_audit(
                conn,
                ticket_id=ticket_id,
                node_id=node_id,
                action="dispatch",
                operator=operator_text,
                reason="dispatch next ready node",
                target_status="running",
                detail={
                    "assigned_agent_id": agent_id,
                    "priority": int(candidate.get("priority") or 0),
                },
                created_at=now_text,
            )
            dispatched.append({"node_id": node_id, "audit_id": audit_id})
        _refresh_pause_state(conn, ticket_id, now_text)
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    _sync_assignment_workspace_snapshot(root, snapshot)
    dispatched_nodes = [
        node
        for node in snapshot["serialized_nodes"]
        if str(node.get("node_id") or "").strip() in {item["node_id"] for item in dispatched}
    ]
    return {
        "ticket_id": ticket_id,
        "dispatched": dispatched_nodes,
        "skipped": skipped,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
    }


def pause_assignment_scheduler(
    root: Path,
    *,
    ticket_id_text: str,
    operator: str,
    pause_note: Any = "",
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    if not ticket_id:
        raise AssignmentCenterError(400, "ticket_id required", "ticket_id_required")
    operator_text = _default_assignment_operator(operator)
    note_text = _normalize_text(pause_note, field="pause_note", required=False, max_len=500)
    now_text = iso_ts(now_local())
    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
        running_count = int(
            (
                conn.execute(
                    """
                    SELECT COUNT(1) AS cnt
                    FROM assignment_nodes
                    WHERE ticket_id=? AND status='running'
                    """,
                    (ticket_id,),
                ).fetchone()
                or {"cnt": 0}
            )["cnt"]
        )
        next_state = "pause_pending" if running_count > 0 else "paused"
        conn.execute(
            """
            UPDATE assignment_graphs
            SET scheduler_state=?,pause_note=?,updated_at=?
            WHERE ticket_id=?
            """,
            (next_state, note_text, now_text, ticket_id),
        )
        audit_id = _write_assignment_audit(
            conn,
            ticket_id=ticket_id,
            node_id="",
            action="pause_scheduler",
            operator=operator_text,
            reason=note_text or "pause scheduler",
            target_status=next_state,
            detail={"running_count": running_count},
            created_at=now_text,
        )
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    _sync_assignment_workspace_snapshot(root, snapshot)
    return {
        "ticket_id": ticket_id,
        "state": next_state,
        "state_text": _scheduler_state_text(next_state),
        "pause_note": note_text,
        "audit_id": audit_id,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
    }


def resume_assignment_scheduler(
    root: Path,
    *,
    ticket_id_text: str,
    operator: str,
    pause_note: Any = "",
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    if not ticket_id:
        raise AssignmentCenterError(400, "ticket_id required", "ticket_id_required")
    operator_text = _default_assignment_operator(operator)
    note_text = _normalize_text(pause_note, field="pause_note", required=False, max_len=500)
    now_text = iso_ts(now_local())
    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
        conn.execute(
            """
            UPDATE assignment_graphs
            SET scheduler_state='running',pause_note=?,updated_at=?
            WHERE ticket_id=?
            """,
            (note_text, now_text, ticket_id),
        )
        audit_id = _write_assignment_audit(
            conn,
            ticket_id=ticket_id,
            node_id="",
            action="resume_scheduler",
            operator=operator_text,
            reason=note_text or "resume scheduler",
            target_status="running",
            detail={},
            created_at=now_text,
        )
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    _sync_assignment_workspace_snapshot(root, snapshot)
    return {
        "ticket_id": ticket_id,
        "state": "running",
        "state_text": _scheduler_state_text("running"),
        "pause_note": note_text,
        "audit_id": audit_id,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
    }


def clear_assignment_graph(
    root: Path,
    *,
    ticket_id_text: str,
    operator: str,
    reason: Any = "",
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    if not ticket_id:
        raise AssignmentCenterError(400, "ticket_id required", "ticket_id_required")
    operator_text = _default_assignment_operator(operator)
    reason_text = _normalize_text(reason, field="reason", required=False, max_len=1000)
    now_text = iso_ts(now_local())
    removed_nodes: list[dict[str, Any]] = []
    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
        snapshot_before = _current_assignment_snapshot(conn, ticket_id)
        removed_nodes = list(snapshot_before.get("serialized_nodes") or [])
        running_nodes = [
            node
            for node in removed_nodes
            if str(node.get("status") or "").strip().lower() == "running"
        ]
        if running_nodes:
            raise AssignmentCenterError(
                409,
                "running nodes prevent clear",
                "assignment_clear_has_running_nodes",
                {
                    "running_node_ids": [
                        str(node.get("node_id") or "").strip()
                        for node in running_nodes
                    ],
                },
            )
        removed_edge_count = int(
            conn.execute(
                "DELETE FROM assignment_edges WHERE ticket_id=?",
                (ticket_id,),
            ).rowcount
            or 0
        )
        removed_node_count = int(
            conn.execute(
                "DELETE FROM assignment_nodes WHERE ticket_id=?",
                (ticket_id,),
            ).rowcount
            or 0
        )
        conn.execute(
            """
            UPDATE assignment_graphs
            SET scheduler_state='idle',pause_note='',updated_at=?
            WHERE ticket_id=?
            """,
            (now_text, ticket_id),
        )
        audit_id = _write_assignment_audit(
            conn,
            ticket_id=ticket_id,
            node_id="",
            action="clear_graph",
            operator=operator_text,
            reason=reason_text or "clear assignment graph",
            target_status="idle",
            detail={
                "removed_node_count": removed_node_count,
                "removed_edge_count": removed_edge_count,
                "removed_node_ids": [
                    str(node.get("node_id") or "").strip()
                    for node in removed_nodes[:100]
                ],
            },
            created_at=now_text,
        )
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    for node in removed_nodes:
        _persist_assignment_workspace_node(
            root,
            node=node,
            record_state="deleted",
            audit_id=audit_id,
            extra={
                "delete_action": "clear_graph",
                "deleted_at": now_text,
                "delete_reason": reason_text or "clear assignment graph",
            },
        )
    _persist_assignment_workspace_graph(
        root,
        snapshot=snapshot,
        record_state="active",
        extra={
            "last_graph_action": "clear_graph",
            "last_graph_action_at": now_text,
            "audit_ref": _db_ref(audit_id),
        },
    )
    return {
        "ticket_id": ticket_id,
        "removed_node_count": removed_node_count,
        "removed_edge_count": removed_edge_count,
        "audit_id": audit_id,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
    }


def delete_assignment_node(
    root: Path,
    *,
    ticket_id_text: str,
    node_id_text: str,
    operator: str,
    reason: Any = "",
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    node_id = safe_token(str(node_id_text or ""), "", 160)
    if not ticket_id or not node_id:
        raise AssignmentCenterError(400, "ticket_id/node_id required", "ticket_or_node_required")
    operator_text = _default_assignment_operator(operator)
    reason_text = _normalize_text(reason, field="reason", required=False, max_len=1000)
    now_text = iso_ts(now_local())
    deleted_node_serialized: dict[str, Any] = {}
    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_ticket_node_row_visible(conn, ticket_id, node_id, include_test_data=include_test_data)
        snapshot_before = _current_assignment_snapshot(conn, ticket_id)
        deleted_node_serialized = next(
            (
                node
                for node in list(snapshot_before.get("serialized_nodes") or [])
                if str(node.get("node_id") or "").strip() == node_id
            ),
            {},
        )
        current_status = str(deleted_node_serialized.get("status") or "").strip().lower()
        if current_status == "running":
            raise AssignmentCenterError(
                409,
                "running node cannot be deleted",
                "assignment_delete_running_node_blocked",
                {"node_id": node_id},
            )
        bridge_plan = _plan_bridge_edges_after_delete(
            node_id=node_id,
            nodes=list(snapshot_before.get("nodes") or []),
            edges=list(snapshot_before.get("edges") or []),
        )
        removed_edge_count = int(
            conn.execute(
                """
                DELETE FROM assignment_edges
                WHERE ticket_id=? AND (from_node_id=? OR to_node_id=?)
                """,
                (ticket_id, node_id, node_id),
            ).rowcount
            or 0
        )
        conn.execute(
            "DELETE FROM assignment_nodes WHERE ticket_id=? AND node_id=?",
            (ticket_id, node_id),
        )
        bridge_edges = [
            (
                str(item.get("from_node_id") or "").strip(),
                str(item.get("to_node_id") or "").strip(),
            )
            for item in list(bridge_plan.get("bridge_added") or [])
            if str(item.get("from_node_id") or "").strip()
            and str(item.get("to_node_id") or "").strip()
        ]
        if bridge_edges:
            _insert_edges(conn, ticket_id=ticket_id, edges=bridge_edges, created_at=now_text)
        _recompute_graph_statuses(conn, ticket_id)
        remaining_nodes = _load_nodes(conn, ticket_id)
        if not remaining_nodes:
            conn.execute(
                """
                UPDATE assignment_graphs
                SET scheduler_state='idle',pause_note='',updated_at=?
                WHERE ticket_id=?
                """,
                (now_text, ticket_id),
            )
        audit_id = _write_assignment_audit(
            conn,
            ticket_id=ticket_id,
            node_id=node_id,
            action="delete_node",
            operator=operator_text,
            reason=reason_text or "delete assignment node",
            target_status="deleted",
            detail={
                "removed_edge_count": removed_edge_count,
                "deleted_node": {
                    "node_id": str(deleted_node_serialized.get("node_id") or "").strip(),
                    "node_name": str(deleted_node_serialized.get("node_name") or "").strip(),
                    "status": current_status,
                },
                "bridge_summary": bridge_plan,
            },
            created_at=now_text,
        )
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    _persist_assignment_workspace_node(
        root,
        node=deleted_node_serialized,
        record_state="deleted",
        audit_id=audit_id,
        extra={
            "delete_action": "delete_node",
            "deleted_at": now_text,
            "delete_reason": reason_text or "delete assignment node",
            "bridge_summary": bridge_plan,
        },
    )
    _sync_assignment_workspace_snapshot(root, snapshot)
    return {
        "ticket_id": ticket_id,
        "deleted_node_id": node_id,
        "removed_edge_count": removed_edge_count,
        "bridge_summary": bridge_plan,
        "audit_id": audit_id,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
    }


def _ensure_ticket_node_row(conn: sqlite3.Connection, ticket_id: str, node_id: str) -> sqlite3.Row:
    row = conn.execute(
        """
        SELECT
            node_id,ticket_id,node_name,assigned_agent_id,status,priority,
            completed_at,success_reason,result_ref,failure_reason,created_at,updated_at
        FROM assignment_nodes
        WHERE ticket_id=? AND node_id=?
        LIMIT 1
        """,
        (ticket_id, node_id),
    ).fetchone()
    if row is None:
        raise AssignmentCenterError(
            404,
            "assignment node not found",
            "assignment_node_not_found",
            {"ticket_id": ticket_id, "node_id": node_id},
        )
    return row


def _ensure_ticket_node_row_visible(
    conn: sqlite3.Connection,
    ticket_id: str,
    node_id: str,
    *,
    include_test_data: bool,
) -> sqlite3.Row:
    _ensure_graph_row_visible(conn, ticket_id, include_test_data=include_test_data)
    return _ensure_ticket_node_row(conn, ticket_id, node_id)


def mark_assignment_node_success(
    root: Path,
    *,
    ticket_id_text: str,
    node_id_text: str,
    success_reason: Any,
    result_ref: Any = "",
    operator: str,
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    node_id = safe_token(str(node_id_text or ""), "", 160)
    if not ticket_id or not node_id:
        raise AssignmentCenterError(400, "ticket_id/node_id required", "ticket_or_node_required")
    success_text = _normalize_text(success_reason, field="success_reason", required=True, max_len=1000)
    result_ref_text = _normalize_text(result_ref, field="result_ref", required=False, max_len=500)
    operator_text = _default_assignment_operator(operator)
    now_text = iso_ts(now_local())
    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = _ensure_ticket_node_row_visible(conn, ticket_id, node_id, include_test_data=include_test_data)
        snapshot_before = _current_assignment_snapshot(conn, ticket_id)
        selected_node = snapshot_before["node_map_by_id"].get(node_id) or _row_dict(row)
        current_status = str(row["status"] or "").strip().lower()
        if current_status != "running":
            raise AssignmentCenterError(
                409,
                "mark-success only allowed when node is running",
                "mark_success_status_invalid",
                {"current_status": current_status},
            )
        if str(selected_node.get("artifact_delivery_status") or "").strip().lower() != "delivered":
            raise AssignmentCenterError(
                409,
                "artifact delivery required before success",
                "artifact_delivery_required",
                {"artifact_delivery_status": str(selected_node.get("artifact_delivery_status") or "pending")},
            )
        conn.execute(
            """
            UPDATE assignment_nodes
            SET status='succeeded',
                completed_at=?,
                success_reason=?,
                result_ref=?,
                failure_reason='',
                updated_at=?
            WHERE ticket_id=? AND node_id=?
            """,
            (now_text, success_text, result_ref_text, now_text, ticket_id, node_id),
        )
        _recompute_graph_statuses(conn, ticket_id)
        audit_id = _write_assignment_audit(
            conn,
            ticket_id=ticket_id,
            node_id=node_id,
            action="mark_success",
            operator=operator_text,
            reason=success_text,
            target_status="succeeded",
            detail={"result_ref": result_ref_text},
            created_at=now_text,
        )
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    _sync_assignment_workspace_snapshot(root, snapshot)
    selected_node = next(
        (node for node in snapshot["serialized_nodes"] if str(node.get("node_id") or "").strip() == node_id),
        {},
    )
    return {
        "ticket_id": ticket_id,
        "node": selected_node,
        "audit_id": audit_id,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
    }


def mark_assignment_node_failed(
    root: Path,
    *,
    ticket_id_text: str,
    node_id_text: str,
    failure_reason: Any,
    operator: str,
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    node_id = safe_token(str(node_id_text or ""), "", 160)
    if not ticket_id or not node_id:
        raise AssignmentCenterError(400, "ticket_id/node_id required", "ticket_or_node_required")
    failure_text = _normalize_text(failure_reason, field="failure_reason", required=True, max_len=1000)
    operator_text = _default_assignment_operator(operator)
    now_text = iso_ts(now_local())
    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = _ensure_ticket_node_row_visible(conn, ticket_id, node_id, include_test_data=include_test_data)
        current_status = str(row["status"] or "").strip().lower()
        if current_status != "running":
            raise AssignmentCenterError(
                409,
                "mark-failed only allowed when node is running",
                "mark_failed_status_invalid",
                {"current_status": current_status},
            )
        conn.execute(
            """
            UPDATE assignment_nodes
            SET status='failed',
                completed_at=?,
                success_reason='',
                result_ref='',
                failure_reason=?,
                updated_at=?
            WHERE ticket_id=? AND node_id=?
            """,
            (now_text, failure_text, now_text, ticket_id, node_id),
        )
        _recompute_graph_statuses(conn, ticket_id)
        audit_id = _write_assignment_audit(
            conn,
            ticket_id=ticket_id,
            node_id=node_id,
            action="mark_failed",
            operator=operator_text,
            reason=failure_text,
            target_status="failed",
            detail={},
            created_at=now_text,
        )
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    _sync_assignment_workspace_snapshot(root, snapshot)
    selected_node = next(
        (node for node in snapshot["serialized_nodes"] if str(node.get("node_id") or "").strip() == node_id),
        {},
    )
    return {
        "ticket_id": ticket_id,
        "node": selected_node,
        "audit_id": audit_id,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
    }


def rerun_assignment_node(
    root: Path,
    *,
    ticket_id_text: str,
    node_id_text: str,
    operator: str,
    reason: Any = "",
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    node_id = safe_token(str(node_id_text or ""), "", 160)
    if not ticket_id or not node_id:
        raise AssignmentCenterError(400, "ticket_id/node_id required", "ticket_or_node_required")
    operator_text = _default_assignment_operator(operator)
    reason_text = _normalize_text(reason, field="reason", required=False, max_len=500)
    now_text = iso_ts(now_local())
    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = _ensure_ticket_node_row_visible(conn, ticket_id, node_id, include_test_data=include_test_data)
        current_status = str(row["status"] or "").strip().lower()
        if current_status != "failed":
            raise AssignmentCenterError(
                409,
                "rerun only allowed for failed node",
                "rerun_status_invalid",
                {"current_status": current_status},
            )
        conn.execute(
            """
            UPDATE assignment_nodes
            SET status='pending',
                completed_at='',
                success_reason='',
                result_ref='',
                failure_reason='',
                artifact_delivery_status='pending',
                artifact_delivered_at='',
                artifact_paths_json='[]',
                updated_at=?
            WHERE ticket_id=? AND node_id=?
            """,
            (now_text, ticket_id, node_id),
        )
        _recompute_graph_statuses(conn, ticket_id)
        audit_id = _write_assignment_audit(
            conn,
            ticket_id=ticket_id,
            node_id=node_id,
            action="rerun",
            operator=operator_text,
            reason=reason_text or "rerun failed node",
            target_status="pending",
            detail={},
            created_at=now_text,
        )
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    _sync_assignment_workspace_snapshot(root, snapshot)
    selected_node = next(
        (node for node in snapshot["serialized_nodes"] if str(node.get("node_id") or "").strip() == node_id),
        {},
    )
    return {
        "ticket_id": ticket_id,
        "node": selected_node,
        "audit_id": audit_id,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
    }


def override_assignment_node_status(
    root: Path,
    *,
    ticket_id_text: str,
    node_id_text: str,
    target_status: Any,
    operator: str,
    reason: Any,
    include_test_data: bool = True,
) -> dict[str, Any]:
    ticket_id = safe_token(str(ticket_id_text or ""), "", 160)
    node_id = safe_token(str(node_id_text or ""), "", 160)
    if not ticket_id or not node_id:
        raise AssignmentCenterError(400, "ticket_id/node_id required", "ticket_or_node_required")
    next_status = _normalize_status(target_status, field="target_status")
    operator_text = _default_assignment_operator(operator)
    reason_text = _normalize_text(reason, field="reason", required=True, max_len=1000)
    now_text = iso_ts(now_local())
    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = _ensure_ticket_node_row_visible(conn, ticket_id, node_id, include_test_data=include_test_data)
        snapshot_before = _current_assignment_snapshot(conn, ticket_id)
        selected_node = snapshot_before["node_map_by_id"].get(node_id) or _row_dict(row)
        current_status = str(selected_node.get("status") or row["status"] or "").strip().lower()
        if current_status != "failed":
            raise AssignmentCenterError(
                409,
                "override-status only allowed when node is failed",
                "override_status_only_for_failed",
                {"current_status": current_status},
            )
        blocking_reasons = _node_blocking_reasons(
            node_id,
            node_map_by_id=snapshot_before["node_map_by_id"],
            upstream_map=snapshot_before["upstream_map"],
        )
        if next_status == "running":
            if blocking_reasons:
                raise AssignmentCenterError(
                    409,
                    "override to running blocked by upstream",
                    "override_running_blocked_by_upstream",
                    {"blocking_reasons": blocking_reasons},
                )
            graph_row = snapshot_before["graph_row"]
            scheduler_state = str(graph_row["scheduler_state"] or "").strip().lower()
            if scheduler_state != "running":
                raise AssignmentCenterError(
                    409,
                    "scheduler not running",
                    "scheduler_not_running",
                    {"scheduler_state": scheduler_state},
                )
            system_limit, _updated_at = _get_global_concurrency_limit(conn)
            counts = _running_counts(conn, ticket_id=ticket_id)
            graph_limit = int(graph_row["global_concurrency_limit"] or 0)
            effective_limit = _graph_effective_limit(graph_limit=graph_limit, system_limit=system_limit)
            already_running = current_status == "running"
            graph_running = int(counts["graph_running_node_count"]) - (1 if already_running else 0)
            system_running = int(counts["system_running_node_count"]) - (1 if already_running else 0)
            if graph_running >= effective_limit or system_running >= system_limit:
                raise AssignmentCenterError(
                    409,
                    "concurrency limit reached",
                    "concurrency_limit_reached",
                )
            other = conn.execute(
                """
                SELECT node_id
                FROM assignment_nodes
                WHERE status='running'
                  AND assigned_agent_id=?
                  AND node_id<>?
                LIMIT 1
                """,
                (str(selected_node.get("assigned_agent_id") or ""), node_id),
            ).fetchone()
            if other is not None:
                raise AssignmentCenterError(
                    409,
                    "assigned agent already has running node",
                    "assigned_agent_busy",
                    {"running_node_id": str(other["node_id"] or "").strip()},
                )
        if next_status == "ready" and blocking_reasons:
            raise AssignmentCenterError(
                409,
                "override to ready blocked by upstream",
                "override_ready_blocked_by_upstream",
                {"blocking_reasons": blocking_reasons},
            )
        if next_status == "succeeded" and str(selected_node.get("artifact_delivery_status") or "").strip().lower() != "delivered":
            raise AssignmentCenterError(
                409,
                "artifact delivery required before success",
                "artifact_delivery_required",
                {"artifact_delivery_status": str(selected_node.get("artifact_delivery_status") or "pending")},
            )
        completed_at = ""
        success_reason = ""
        result_ref = ""
        failure_reason = ""
        if next_status == "succeeded":
            completed_at = now_text
            success_reason = "override: " + reason_text
        elif next_status == "failed":
            completed_at = now_text
            failure_reason = "override: " + reason_text
        conn.execute(
            """
            UPDATE assignment_nodes
            SET status=?,
                completed_at=?,
                success_reason=?,
                result_ref=?,
                failure_reason=?,
                updated_at=?
            WHERE ticket_id=? AND node_id=?
            """,
            (
                next_status,
                completed_at,
                success_reason,
                result_ref,
                failure_reason,
                now_text,
                ticket_id,
                node_id,
            ),
        )
        sticky = {node_id} if next_status in {"pending", "ready", "blocked"} else set()
        _recompute_graph_statuses(conn, ticket_id, sticky_node_ids=sticky)
        audit_id = _write_assignment_audit(
            conn,
            ticket_id=ticket_id,
            node_id=node_id,
            action="override_status",
            operator=operator_text,
            reason=reason_text,
            target_status=next_status,
            detail={"from_status": current_status},
            created_at=now_text,
        )
        snapshot = _current_assignment_snapshot(conn, ticket_id)
        conn.commit()
    finally:
        conn.close()
    _sync_assignment_workspace_snapshot(root, snapshot)
    updated_node = next(
        (node for node in snapshot["serialized_nodes"] if str(node.get("node_id") or "").strip() == node_id),
        {},
    )
    return {
        "ticket_id": ticket_id,
        "node": updated_node,
        "audit_id": audit_id,
        "graph_overview": _graph_overview_payload(
            snapshot["graph_row"],
            metrics_summary=snapshot["metrics_summary"],
            scheduler_state_payload=snapshot["scheduler"],
        ),
    }
