from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .defect_service import (
    DEFECT_PROCESS_ACTION_KIND,
    DEFECT_REVIEW_ACTION_KIND,
    DEFECT_STATUS_DISPUTE,
    DefectCenterError,
    _append_history,
    _defect_manual_task_gate,
    _default_assignee,
    _ensure_defect_tables,
    _json_loads_object,
    _load_report_row,
    _normalize_text,
    _now_text,
    _report_row_to_payload,
    _require_report_id,
    _runtime_version_label,
    _status_text,
    _write_report_update,
    assignment_service,
    connect_db,
    get_defect_detail,
)


def _task_ref_id(
    report_id: str,
    ticket_id: str,
    focus_node_id: str,
    action_kind: str,
    external_request_id: str,
) -> str:
    raw = "|".join(
        [
            str(report_id or "").strip(),
            str(ticket_id or "").strip(),
            str(focus_node_id or "").strip(),
            str(action_kind or "").strip(),
            str(external_request_id or "").strip(),
        ]
    )
    return "dtr-" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _upsert_task_ref(
    conn,
    report_id: str,
    *,
    ticket_id: str,
    focus_node_id: str,
    action_kind: str,
    title: str,
    external_request_id: str,
    created_at: str,
) -> None:
    row = conn.execute(
        """
        SELECT ref_id,created_at FROM defect_task_refs
        WHERE report_id=? AND ticket_id=? AND focus_node_id=? AND external_request_id=?
        LIMIT 1
        """,
        (report_id, ticket_id, focus_node_id, external_request_id),
    ).fetchone()
    if row is None:
        conn.execute(
            """
            INSERT INTO defect_task_refs(
                ref_id,report_id,ticket_id,focus_node_id,action_kind,title,external_request_id,created_at,updated_at
            )
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                _task_ref_id(report_id, ticket_id, focus_node_id, action_kind, external_request_id),
                report_id,
                ticket_id,
                focus_node_id,
                action_kind,
                title,
                external_request_id,
                created_at,
                created_at,
            ),
        )
        return
    conn.execute(
        """
        UPDATE defect_task_refs
        SET action_kind=?, title=?, updated_at=?
        WHERE ref_id=?
        """,
        (
            action_kind,
            title,
            created_at,
            str(row["ref_id"] or "").strip(),
        ),
    )


def create_defect_process_task(
    cfg: Any,
    report_id: str,
    body: dict[str, Any],
    *,
    include_test_data: bool = True,
) -> dict[str, Any]:
    root = Path(cfg.root)
    _ensure_defect_tables(root)
    report_key = _require_report_id(report_id)
    operator = _normalize_text(body.get("operator") or "web-user", field="operator", required=False, max_len=120) or "web-user"
    auto_queue = str(body.get("auto_queue") or "").strip().lower() in {"1", "true", "yes", "on"}
    assignee = _normalize_text(body.get("assigned_agent_id") or body.get("assignedAgentId") or _default_assignee(cfg), field="assigned_agent_id", required=True, max_len=120)
    now_text = _now_text()
    external_request_id = f"defect:process:{report_key}"
    analyze_node_id = f"{report_key}-analyze"
    fix_node_id = f"{report_key}-fix"
    release_node_id = f"{report_key}-release"
    if not auto_queue:
        gate = _defect_manual_task_gate(root, report_key, include_test_data=include_test_data)
        if not bool(gate.get("allowed")):
            raise DefectCenterError(
                409,
                "defect queue gate blocked manual task creation",
                "defect_queue_gate_blocked",
                gate,
            )
    conn = connect_db(root)
    try:
        conn.execute("BEGIN")
        row = _load_report_row(conn, report_key, include_test_data=include_test_data)
        if not bool(row["is_formal"]):
            raise DefectCenterError(409, "not a formal defect yet", "defect_process_requires_formal")
        report = _report_row_to_payload(row)
        priority_label = str(report.get("task_priority") or "P1").strip() or "P1"
        graph_result = assignment_service.create_assignment_graph(
            cfg,
            {
                "graph_name": f"{str(row['dts_id'] or report_key).strip()} 缺陷处理",
                "summary": str(row["defect_summary"] or "").strip(),
                "source_workflow": "defect-center",
                "review_mode": "none",
                "external_request_id": external_request_id,
                "is_test_data": bool(row["is_test_data"]),
                "nodes": [
                    {
                        "node_id": analyze_node_id,
                        "node_name": "分析缺陷",
                        "assigned_agent_id": assignee,
                        "node_goal": "分析当前缺陷成因、复现条件和修复范围。",
                        "expected_artifact": "分析缺陷报告.html",
                        "priority": priority_label,
                        "delivery_mode": "specified",
                        "delivery_receiver_agent_id": assignee,
                    },
                    {
                        "node_id": fix_node_id,
                        "node_name": "修复缺陷",
                        "assigned_agent_id": assignee,
                        "node_goal": "完成缺陷修复并输出修复说明。",
                        "expected_artifact": "缺陷修复说明.html",
                        "priority": priority_label,
                        "upstream_node_ids": [analyze_node_id],
                        "delivery_mode": "specified",
                        "delivery_receiver_agent_id": assignee,
                    },
                    {
                        "node_id": release_node_id,
                        "node_name": "推送到目标版本",
                        "assigned_agent_id": assignee,
                        "node_goal": "确认修复进入目标版本并产出发布记录。",
                        "expected_artifact": "目标版本发布记录.html",
                        "priority": priority_label,
                        "upstream_node_ids": [fix_node_id],
                        "delivery_mode": "specified",
                        "delivery_receiver_agent_id": assignee,
                    },
                ],
            },
        )
        ticket_id = str(graph_result.get("ticket_id") or "").strip()
        if not ticket_id:
            raise DefectCenterError(500, "process task created without ticket_id", "defect_process_ticket_missing")
        for focus_node_id, title in (
            (analyze_node_id, "分析缺陷"),
            (fix_node_id, "修复缺陷"),
            (release_node_id, "推送到目标版本"),
        ):
            _upsert_task_ref(
                conn,
                report_key,
                ticket_id=ticket_id,
                focus_node_id=focus_node_id,
                action_kind=DEFECT_PROCESS_ACTION_KIND,
                title=title,
                external_request_id=external_request_id,
                created_at=now_text,
            )
        _append_history(
            conn,
            report_key,
            entry_type="task",
            actor=operator,
            title="已在任务中心创建处理任务",
            detail={
                "ticket_id": ticket_id,
                "external_request_id": external_request_id,
                "assigned_agent_id": assignee,
                "task_priority": priority_label,
                "auto_queue": auto_queue,
            },
            created_at=now_text,
        )
        conn.execute("UPDATE defect_reports SET updated_at=? WHERE report_id=?", (now_text, report_key))
        conn.commit()
    finally:
        conn.close()
    detail = get_defect_detail(root, report_key, include_test_data=include_test_data)
    detail["created_task_ticket_id"] = ticket_id
    detail["external_request_id"] = external_request_id
    return detail


def create_defect_review_task(
    cfg: Any,
    report_id: str,
    body: dict[str, Any],
    *,
    include_test_data: bool = True,
) -> dict[str, Any]:
    root = Path(cfg.root)
    _ensure_defect_tables(root)
    report_key = _require_report_id(report_id)
    operator = _normalize_text(body.get("operator") or "web-user", field="operator", required=False, max_len=120) or "web-user"
    auto_queue = str(body.get("auto_queue") or "").strip().lower() in {"1", "true", "yes", "on"}
    assignee = _normalize_text(body.get("assigned_agent_id") or body.get("assignedAgentId") or _default_assignee(cfg), field="assigned_agent_id", required=True, max_len=120)
    now_text = _now_text()
    external_request_id = f"defect:review:{report_key}"
    review_node_id = f"{report_key}-review"
    if not auto_queue:
        gate = _defect_manual_task_gate(root, report_key, include_test_data=include_test_data)
        if not bool(gate.get("allowed")):
            raise DefectCenterError(
                409,
                "defect queue gate blocked manual review creation",
                "defect_queue_gate_blocked",
                gate,
            )
    conn = connect_db(root)
    try:
        conn.execute("BEGIN")
        row = _load_report_row(conn, report_key, include_test_data=include_test_data)
        payload = _report_row_to_payload(row)
        dts_id = str(payload.get("dts_id") or report_key).strip()
        priority_label = str(payload.get("task_priority") or "P1").strip() or "P1"
        if str(row["status"] or "").strip().lower() != DEFECT_STATUS_DISPUTE:
            current_decision = _json_loads_object(row["current_decision_json"])
            current_decision.update(
                {
                    "decision": "dispute",
                    "decision_source": str(current_decision.get("decision_source") or "review_request").strip() or "review_request",
                    "title": "用户已提出分歧",
                    "summary": "已进入复核链路。",
                }
            )
            discovered_iteration = str(row["discovered_iteration"] or "").strip() or _runtime_version_label()
            _write_report_update(
                conn,
                report_key,
                status=DEFECT_STATUS_DISPUTE,
                discovered_iteration=discovered_iteration,
                current_decision=current_decision,
                updated_at=now_text,
            )
            if not dts_id:
                dts_id = str(row["report_id"] or report_key).strip()
        graph_result = assignment_service.create_assignment_graph(
            cfg,
            {
                "graph_name": f"{dts_id} 争议复核",
                "summary": str(row["defect_summary"] or "").strip(),
                "source_workflow": "defect-center-review",
                "review_mode": "none",
                "external_request_id": external_request_id,
                "is_test_data": bool(row["is_test_data"]),
                "nodes": [
                    {
                        "node_id": review_node_id,
                        "node_name": "复核争议",
                        "assigned_agent_id": assignee,
                        "node_goal": "结合补充证据和当前结论完成复核。",
                        "expected_artifact": "复核争议结论.html",
                        "priority": priority_label,
                        "delivery_mode": "specified",
                        "delivery_receiver_agent_id": assignee,
                    }
                ],
            },
        )
        ticket_id = str(graph_result.get("ticket_id") or "").strip()
        if not ticket_id:
            raise DefectCenterError(500, "review task created without ticket_id", "defect_review_ticket_missing")
        _upsert_task_ref(
            conn,
            report_key,
            ticket_id=ticket_id,
            focus_node_id=review_node_id,
            action_kind=DEFECT_REVIEW_ACTION_KIND,
            title="复核争议",
            external_request_id=external_request_id,
            created_at=now_text,
        )
        _append_history(
            conn,
            report_key,
            entry_type="task",
            actor=operator,
            title="已在任务中心创建复核任务",
            detail={
                "ticket_id": ticket_id,
                "external_request_id": external_request_id,
                "assigned_agent_id": assignee,
                "status_text": _status_text(DEFECT_STATUS_DISPUTE),
                "task_priority": priority_label,
                "auto_queue": auto_queue,
            },
            created_at=now_text,
        )
        conn.execute("UPDATE defect_reports SET updated_at=? WHERE report_id=?", (now_text, report_key))
        conn.commit()
    finally:
        conn.close()
    detail = get_defect_detail(root, report_key, include_test_data=include_test_data)
    detail["created_task_ticket_id"] = ticket_id
    detail["external_request_id"] = external_request_id
    return detail
