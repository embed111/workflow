from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from ..infra.db.connection import connect_db
from . import assignment_service, runtime_upgrade_service


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


class DefectCenterError(RuntimeError):
    def __init__(
        self,
        status_code: int,
        message: str,
        code: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = int(status_code)
        self.code = str(code or "defect_error")
        self.extra = dict(extra or {})


DEFECT_STATUS_NOT_FORMAL = "not_formal"
DEFECT_STATUS_UNRESOLVED = "unresolved"
DEFECT_STATUS_RESOLVED = "resolved"
DEFECT_STATUS_CLOSED = "closed"
DEFECT_STATUS_DISPUTE = "dispute"

DEFECT_ALL_STATUSES = {
    DEFECT_STATUS_NOT_FORMAL,
    DEFECT_STATUS_UNRESOLVED,
    DEFECT_STATUS_RESOLVED,
    DEFECT_STATUS_CLOSED,
    DEFECT_STATUS_DISPUTE,
}

DEFECT_STATUS_TEXT = {
    DEFECT_STATUS_NOT_FORMAL: "当前不构成缺陷",
    DEFECT_STATUS_UNRESOLVED: "未解决",
    DEFECT_STATUS_RESOLVED: "已解决",
    DEFECT_STATUS_CLOSED: "已关闭",
    DEFECT_STATUS_DISPUTE: "有分歧",
}

DEFECT_PROCESS_ACTION_KIND = "process"
DEFECT_REVIEW_ACTION_KIND = "review"


def _now_text() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _date_key() -> str:
    return datetime.now().astimezone().strftime("%Y%m%d")


def _safe_token(value: Any, *, max_len: int = 160) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    out = []
    for ch in text[:max_len]:
        if ch.isalnum() or ch in {"-", "_", ".", ":"}:
            out.append(ch)
    return "".join(out)


def _json_dumps(payload: Any, fallback: str) -> str:
    try:
        return json.dumps(payload, ensure_ascii=False, indent=None)
    except Exception:
        return fallback


def _json_loads_object(raw: Any) -> dict[str, Any]:
    text = str(raw or "").strip()
    if not text:
        return {}
    try:
        payload = json.loads(text)
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _json_loads_list(raw: Any) -> list[Any]:
    text = str(raw or "").strip()
    if not text:
        return []
    try:
        payload = json.loads(text)
    except Exception:
        return []
    return payload if isinstance(payload, list) else []


def _bool_flag(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    return text in {"1", "true", "yes", "y", "on"}


def _defect_report_id() -> str:
    return f"dr-{_date_key()}-{uuid.uuid4().hex[:10]}"


def _defect_history_id() -> str:
    return f"dh-{_date_key()}-{uuid.uuid4().hex[:10]}"


def _require_report_id(report_id: str) -> str:
    key = _safe_token(report_id, max_len=160)
    if not key:
        raise DefectCenterError(400, "report_id required", "defect_report_id_required")
    return key


def _status_text(status: Any) -> str:
    return DEFECT_STATUS_TEXT.get(str(status or "").strip().lower(), str(status or "").strip() or "-")


def _normalize_text(
    value: Any,
    *,
    field: str,
    required: bool = False,
    max_len: int = 4000,
) -> str:
    text = str(value or "").strip()
    if not text:
        if required:
            raise DefectCenterError(400, f"{field} required", f"{field}_required")
        return ""
    if len(text) > max_len:
        raise DefectCenterError(400, f"{field} too long", f"{field}_too_long", {"max_len": max_len})
    return text


def _derive_summary(summary: Any, report_text: Any) -> str:
    summary_text = str(summary or "").strip()
    if summary_text:
        return summary_text[:120]
    for line in str(report_text or "").splitlines():
        candidate = line.strip()
        if candidate:
            return candidate[:120]
    return "未命名缺陷记录"


def _normalize_image_evidence(raw: Any) -> list[dict[str, Any]]:
    rows = raw if isinstance(raw, list) else []
    out: list[dict[str, Any]] = []
    for item in rows:
        if isinstance(item, str):
            url = item.strip()
            if not url:
                continue
            out.append({"image_id": f"img-{uuid.uuid4().hex[:8]}", "name": "", "url": url})
            continue
        if not isinstance(item, dict):
            continue
        url = str(
            item.get("url")
            or item.get("src")
            or item.get("data_url")
            or item.get("dataUrl")
            or item.get("content")
            or ""
        ).strip()
        if not url:
            continue
        out.append(
            {
                "image_id": _safe_token(item.get("image_id") or item.get("attachment_id") or "", max_len=80)
                or f"img-{uuid.uuid4().hex[:8]}",
                "name": str(item.get("name") or item.get("file_name") or "").strip()[:240],
                "url": url,
            }
        )
    return out


def _ensure_defect_tables(root: Path) -> None:
    conn = connect_db(root)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS defect_reports (
                report_id TEXT PRIMARY KEY,
                dts_id TEXT NOT NULL DEFAULT '',
                dts_sequence INTEGER NOT NULL DEFAULT 0,
                defect_summary TEXT NOT NULL DEFAULT '',
                report_text TEXT NOT NULL DEFAULT '',
                evidence_images_json TEXT NOT NULL DEFAULT '[]',
                is_formal INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'not_formal',
                discovered_iteration TEXT NOT NULL DEFAULT '',
                resolved_version TEXT NOT NULL DEFAULT '',
                current_decision_json TEXT NOT NULL DEFAULT '{}',
                report_source TEXT NOT NULL DEFAULT 'workflow-ui',
                automation_context_json TEXT NOT NULL DEFAULT '{}',
                is_test_data INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_defect_reports_updated ON defect_reports(updated_at DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_defect_reports_status ON defect_reports(is_formal,status,updated_at DESC)")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_defect_reports_dts_id ON defect_reports(dts_id) WHERE dts_id<>''")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_defect_reports_dts_sequence ON defect_reports(dts_sequence) WHERE dts_sequence>0")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS defect_history (
                history_id TEXT PRIMARY KEY,
                report_id TEXT NOT NULL,
                entry_type TEXT NOT NULL,
                actor TEXT NOT NULL DEFAULT '',
                title TEXT NOT NULL DEFAULT '',
                detail_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_defect_history_report_time ON defect_history(report_id,created_at)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS defect_task_refs (
                ref_id TEXT PRIMARY KEY,
                report_id TEXT NOT NULL,
                ticket_id TEXT NOT NULL,
                focus_node_id TEXT NOT NULL DEFAULT '',
                action_kind TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                external_request_id TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_defect_task_refs_report_time ON defect_task_refs(report_id,updated_at DESC)")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_defect_task_refs_unique ON defect_task_refs(report_id,ticket_id,focus_node_id,external_request_id)")
        conn.commit()
    finally:
        conn.close()


def _report_row_to_payload(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
    item = dict(row or {})
    status = str(item.get("status") or DEFECT_STATUS_NOT_FORMAL).strip().lower()
    payload = {
        "report_id": str(item.get("report_id") or "").strip(),
        "dts_id": str(item.get("dts_id") or "").strip(),
        "dts_sequence": int(item.get("dts_sequence") or 0),
        "display_id": str(item.get("dts_id") or item.get("report_id") or "").strip(),
        "defect_summary": str(item.get("defect_summary") or "").strip(),
        "report_text": str(item.get("report_text") or "").strip(),
        "evidence_images": _normalize_image_evidence(_json_loads_list(item.get("evidence_images_json"))),
        "is_formal": bool(item.get("is_formal")),
        "status": status,
        "status_text": _status_text(status),
        "discovered_iteration": str(item.get("discovered_iteration") or "").strip(),
        "resolved_version": str(item.get("resolved_version") or "").strip(),
        "current_decision": _json_loads_object(item.get("current_decision_json")),
        "report_source": str(item.get("report_source") or "").strip(),
        "automation_context": _json_loads_object(item.get("automation_context_json")),
        "is_test_data": bool(item.get("is_test_data")),
        "created_at": str(item.get("created_at") or "").strip(),
        "updated_at": str(item.get("updated_at") or "").strip(),
    }
    payload["decision_title"] = str(payload["current_decision"].get("title") or "").strip()
    payload["decision_summary"] = str(payload["current_decision"].get("summary") or "").strip()
    payload["decision_source"] = str(payload["current_decision"].get("decision_source") or "").strip()
    return payload


def _history_row_to_payload(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
    item = dict(row or {})
    return {
        "history_id": str(item.get("history_id") or "").strip(),
        "report_id": str(item.get("report_id") or "").strip(),
        "entry_type": str(item.get("entry_type") or "").strip(),
        "actor": str(item.get("actor") or "").strip(),
        "title": str(item.get("title") or "").strip(),
        "detail": _json_loads_object(item.get("detail_json")),
        "created_at": str(item.get("created_at") or "").strip(),
    }


def _append_history(
    conn: sqlite3.Connection,
    report_id: str,
    *,
    entry_type: str,
    actor: str,
    title: str,
    detail: dict[str, Any] | None = None,
    created_at: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO defect_history(history_id,report_id,entry_type,actor,title,detail_json,created_at)
        VALUES (?,?,?,?,?,?,?)
        """,
        (
            _defect_history_id(),
            report_id,
            str(entry_type or "").strip(),
            str(actor or "").strip(),
            str(title or "").strip(),
            _json_dumps(detail or {}, "{}"),
            str(created_at or _now_text()),
        ),
    )


def _load_report_row(
    conn: sqlite3.Connection,
    report_id: str,
    *,
    include_test_data: bool,
) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM defect_reports WHERE report_id=? LIMIT 1", (report_id,)).fetchone()
    if row is None:
        raise DefectCenterError(404, "defect report not found", "defect_report_not_found")
    if (not include_test_data) and bool(row["is_test_data"]):
        raise DefectCenterError(404, "defect report not found", "defect_report_not_found")
    return row


def _load_history_rows(conn: sqlite3.Connection, report_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM defect_history WHERE report_id=? ORDER BY created_at ASC, history_id ASC",
        (report_id,),
    ).fetchall()
    return [_history_row_to_payload(row) for row in rows]


def _load_task_ref_rows(conn: sqlite3.Connection, report_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM defect_task_refs WHERE report_id=? ORDER BY updated_at DESC, created_at DESC, ref_id DESC",
        (report_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def _next_dts_identity(conn: sqlite3.Connection) -> tuple[int, str]:
    row = conn.execute("SELECT COALESCE(MAX(dts_sequence), 0) + 1 AS next_sequence FROM defect_reports").fetchone()
    next_sequence = int(row["next_sequence"] if row is not None and row["next_sequence"] is not None else 1)
    return next_sequence, f"DTS-{next_sequence:05d}"


def _runtime_version_label() -> str:
    snapshot = runtime_upgrade_service.runtime_snapshot()
    current_version = str(snapshot.get("current_version") or "").strip()
    if current_version:
        return current_version
    current_rank = str(snapshot.get("current_version_rank") or "").strip()
    if current_rank:
        return current_rank
    env_version = str(os.getenv("WORKFLOW_RUNTIME_VERSION") or "").strip()
    if env_version:
        return env_version
    return "source-" + datetime.now().astimezone().strftime("%Y%m%d")


def _fallback_prejudge(report_text: str, images: list[dict[str, Any]]) -> dict[str, Any]:
    text = str(report_text or "").strip().lower()
    strong_hits = [token for token in ("bug", "异常", "报错", "失败", "无法", "崩溃", "卡死", "空白", "404", "500", "回退", "丢失", "不生效") if token in text]
    weak_hits = [token for token in ("显示", "错位", "慢", "超时", "刷新", "关闭", "升级", "路径", "进度条") if token in text]
    demand_hits = [token for token in ("需求", "建议", "优化", "新增", "希望", "想要") if token in text]
    score = len(strong_hits) * 2 + len(weak_hits) + (1 if images else 0)
    if demand_hits and not strong_hits and score < 3:
        score -= 2
    is_defect = score >= 2
    return {
        "decision_source": "fallback_rule",
        "decision": "defect" if is_defect else "not_defect",
        "title": "构成 workflow 缺陷" if is_defect else "当前不构成 workflow 缺陷",
        "summary": "命中异常/失败类线索，已按真实缺陷进入闭环。" if is_defect else "更像需求、建议或描述不足，先不进入正式缺陷链路。",
        "matched_rules": strong_hits + weak_hits + demand_hits,
        "confidence": "medium",
        "scored_images": len(images),
    }


def _available_agent_names(cfg: Any) -> list[str]:
    items: list[dict[str, Any]] = []
    fn = globals().get("list_available_agents")
    if callable(fn):
        try:
            items = fn(cfg, analyze_policy=False)
        except TypeError:
            try:
                items = fn(cfg)
            except Exception:
                items = []
        except Exception:
            items = []
    names = [str(item.get("agent_name") or item.get("agent_id") or "").strip() for item in items]
    names = [name for name in names if name]
    if names:
        return names
    conn = connect_db(Path(cfg.root))
    try:
        rows = conn.execute(
            """
            SELECT agent_name,agent_id,runtime_status
            FROM agent_registry
            WHERE COALESCE(runtime_status,'idle')<>'creating'
            ORDER BY updated_at DESC, agent_name ASC
            """
        ).fetchall()
        return [
            str(row["agent_name"] or row["agent_id"] or "").strip()
            for row in rows
            if str(row["agent_name"] or row["agent_id"] or "").strip()
        ]
    finally:
        conn.close()


def _default_assignee(cfg: Any) -> str:
    names = _available_agent_names(cfg)
    if not names:
        raise DefectCenterError(409, "no available agent for defect task", "defect_assignee_unavailable")
    for name in names:
        if str(name).strip().lower() == "workflow":
            return name
    return names[0]


def _enrich_task_ref(root: Path, row: dict[str, Any], *, include_test_data: bool) -> dict[str, Any]:
    payload = {
        "ref_id": str(row.get("ref_id") or "").strip(),
        "report_id": str(row.get("report_id") or "").strip(),
        "ticket_id": str(row.get("ticket_id") or "").strip(),
        "focus_node_id": str(row.get("focus_node_id") or "").strip(),
        "action_kind": str(row.get("action_kind") or "").strip(),
        "title": str(row.get("title") or "").strip(),
        "external_request_id": str(row.get("external_request_id") or "").strip(),
        "created_at": str(row.get("created_at") or "").strip(),
        "updated_at": str(row.get("updated_at") or "").strip(),
        "graph_name": "",
        "scheduler_state": "",
        "scheduler_state_text": "",
        "node_name": "",
        "node_status": "",
        "node_status_text": "",
    }
    ticket_id = payload["ticket_id"]
    if not ticket_id:
        return payload
    try:
        overview = assignment_service.get_assignment_overview(root, ticket_id, include_test_data=include_test_data)
        graph = dict(overview.get("graph") or {})
        payload["graph_name"] = str(graph.get("graph_name") or graph.get("ticket_id") or "").strip()
        payload["scheduler_state"] = str(graph.get("scheduler_state") or "").strip()
        payload["scheduler_state_text"] = str(graph.get("scheduler_state_text") or "").strip()
    except Exception:
        return payload
    node_id = payload["focus_node_id"]
    if not node_id:
        return payload
    try:
        status_detail = assignment_service.get_assignment_status_detail(
            root,
            ticket_id,
            node_id_text=node_id,
            include_test_data=include_test_data,
        )
        selected_node = dict(status_detail.get("selected_node") or {})
        payload["node_name"] = str(selected_node.get("node_name") or node_id).strip()
        payload["node_status"] = str(selected_node.get("status") or "").strip()
        payload["node_status_text"] = str(selected_node.get("status_text") or "").strip()
    except Exception:
        payload["node_name"] = node_id
    return payload


def list_defect_reports(
    root: Path,
    *,
    include_test_data: bool = True,
    status_filter: str = "",
    keyword: str = "",
    limit: int = 200,
) -> dict[str, Any]:
    _ensure_defect_tables(root)
    limit_value = max(1, min(500, int(limit or 200)))
    status_key = str(status_filter or "").strip().lower()
    keyword_text = str(keyword or "").strip().lower()
    sql = "SELECT * FROM defect_reports WHERE 1=1"
    params: list[Any] = []
    if not include_test_data:
        sql += " AND is_test_data=0"
    if status_key and status_key != "all":
        sql += " AND status=?"
        params.append(status_key)
    sql += " ORDER BY updated_at DESC, created_at DESC, report_id DESC LIMIT ?"
    params.append(limit_value)
    conn = connect_db(root)
    try:
        rows = conn.execute(sql, tuple(params)).fetchall()
        items = [_report_row_to_payload(row) for row in rows]
        if keyword_text:
            items = [
                item
                for item in items
                if keyword_text in "\n".join(
                    [
                        str(item.get("report_id") or ""),
                        str(item.get("dts_id") or ""),
                        str(item.get("defect_summary") or ""),
                        str(item.get("report_text") or ""),
                        str(item.get("decision_title") or ""),
                        str(item.get("decision_summary") or ""),
                    ]
                ).lower()
            ]
        return {"items": items, "total": len(items), "status_filter": status_key, "keyword": keyword_text}
    finally:
        conn.close()


def get_defect_detail(
    root: Path,
    report_id: str,
    *,
    include_test_data: bool = True,
) -> dict[str, Any]:
    _ensure_defect_tables(root)
    report_key = _require_report_id(report_id)
    conn = connect_db(root)
    try:
        row = _load_report_row(conn, report_key, include_test_data=include_test_data)
        report = _report_row_to_payload(row)
        history = _load_history_rows(conn, report_key)
        task_refs = [_enrich_task_ref(root, item, include_test_data=include_test_data) for item in _load_task_ref_rows(conn, report_key)]
    finally:
        conn.close()
    return {
        "report": report,
        "history": history,
        "task_refs": task_refs,
        "history_total": len(history),
        "task_ref_total": len(task_refs),
        "show_re_review_input": report["status"] in {DEFECT_STATUS_DISPUTE, DEFECT_STATUS_RESOLVED, DEFECT_STATUS_NOT_FORMAL},
        "can_process": bool(report["is_formal"]) and report["status"] in {DEFECT_STATUS_UNRESOLVED, DEFECT_STATUS_DISPUTE},
        "can_review": report["status"] in {DEFECT_STATUS_DISPUTE, DEFECT_STATUS_RESOLVED, DEFECT_STATUS_NOT_FORMAL},
        "can_close": report["status"] == DEFECT_STATUS_RESOLVED,
    }


def get_defect_history(
    root: Path,
    report_id: str,
    *,
    include_test_data: bool = True,
) -> dict[str, Any]:
    detail = get_defect_detail(root, report_id, include_test_data=include_test_data)
    return {"report_id": str(detail["report"]["report_id"]), "history": list(detail["history"]), "total": len(detail["history"])}


def _write_report_update(
    conn: sqlite3.Connection,
    report_id: str,
    *,
    status: str | None = None,
    is_formal: bool | None = None,
    discovered_iteration: str | None = None,
    resolved_version: str | None = None,
    current_decision: dict[str, Any] | None = None,
    updated_at: str | None = None,
) -> None:
    row = _load_report_row(conn, report_id, include_test_data=True)
    next_status = str(status if status is not None else row["status"] or "").strip().lower()
    next_is_formal = bool(row["is_formal"] if is_formal is None else is_formal)
    next_discovered = str(row["discovered_iteration"] or "").strip() if discovered_iteration is None else str(discovered_iteration or "").strip()
    next_resolved = str(row["resolved_version"] or "").strip() if resolved_version is None else str(resolved_version or "").strip()
    next_decision = _json_loads_object(row["current_decision_json"]) if current_decision is None else dict(current_decision or {})
    conn.execute(
        """
        UPDATE defect_reports
        SET status=?, is_formal=?, discovered_iteration=?, resolved_version=?, current_decision_json=?, updated_at=?
        WHERE report_id=?
        """,
        (
            next_status,
            1 if next_is_formal else 0,
            next_discovered,
            next_resolved,
            _json_dumps(next_decision, "{}"),
            str(updated_at or _now_text()),
            report_id,
        ),
    )


def _formalize_report_if_needed(
    conn: sqlite3.Connection,
    report_id: str,
    *,
    actor: str,
    decision_title: str,
    decision_summary: str,
) -> dict[str, Any]:
    row = _load_report_row(conn, report_id, include_test_data=True)
    discovered_iteration = str(row["discovered_iteration"] or "").strip() or _runtime_version_label()
    dts_sequence, dts_id = _next_dts_identity(conn) if not str(row["dts_id"] or "").strip() else (int(row["dts_sequence"] or 0), str(row["dts_id"] or "").strip())
    if not str(row["dts_id"] or "").strip():
        conn.execute("UPDATE defect_reports SET dts_sequence=?, dts_id=? WHERE report_id=?", (dts_sequence, dts_id, report_id))
    current_decision = _json_loads_object(row["current_decision_json"])
    current_decision.update(
        {
            "decision_source": str(current_decision.get("decision_source") or "manual").strip() or "manual",
            "decision": "defect",
            "title": str(decision_title or "已转为正式缺陷").strip(),
            "summary": str(decision_summary or "").strip(),
            "formalized_at": _now_text(),
        }
    )
    _write_report_update(
        conn,
        report_id,
        is_formal=True,
        discovered_iteration=discovered_iteration,
        current_decision=current_decision,
    )
    _append_history(
        conn,
        report_id,
        entry_type="formalized",
        actor=actor,
        title="缺陷已转为正式记录",
        detail={"dts_id": dts_id, "dts_sequence": dts_sequence, "discovered_iteration": discovered_iteration},
    )
    return {"dts_id": dts_id, "dts_sequence": dts_sequence, "discovered_iteration": discovered_iteration}


from .defect_service_record_commands import (  # noqa: E402
    append_defect_images,
    append_defect_text,
    create_defect_report,
    mark_defect_dispute,
    update_defect_status,
    write_defect_resolved_version,
)
from .defect_service_task_commands import (  # noqa: E402
    create_defect_process_task,
    create_defect_review_task,
)
