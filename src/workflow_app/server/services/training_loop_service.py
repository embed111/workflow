from __future__ import annotations

import json
import sqlite3
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


def _parse_loop_graph(raw: object) -> dict[str, Any]:
    if isinstance(raw, dict):
        return dict(raw)
    if not raw:
        return {}
    try:
        payload = json.loads(str(raw))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _json_object(raw: object) -> dict[str, Any]:
    if isinstance(raw, dict):
        return dict(raw)
    if not raw:
        return {}
    try:
        payload = json.loads(str(raw))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _parse_training_tasks(raw: object) -> list[str]:
    try:
        payload = json.loads(str(raw or "[]"))
    except Exception:
        payload = []
    if not isinstance(payload, list):
        return []
    return [str(item or "").strip() for item in payload if str(item or "").strip()]


def _safe_float(raw: object) -> float | None:
    if raw in (None, ""):
        return None
    try:
        return round(float(raw), 2)
    except Exception:
        return None


def _loop_node_base(now_text: str) -> dict[str, Any]:
    return {
        "node_id": "baseline",
        "title": "基线",
        "round_index": 0,
        "round_label": "Baseline",
        "node_type": "baseline",
        "decision": "暂无历史",
        "decision_code": "baseline",
        "next_action": "执行首轮评测",
        "next_action_code": "",
        "impact": "闭环起点",
        "metrics": {
            "avg_score": None,
            "threshold": None,
            "previous_avg_score": None,
            "run_results": [],
        },
        "metrics_available": False,
        "metrics_unavailable_reason": "baseline_without_metrics",
        "queue_task_id": "",
        "plan_id": "",
        "status": "active",
        "available_actions": [],
        "run_ids": [],
        "execution_engine": EXECUTION_ENGINE,
        "created_at": now_text,
        "updated_at": now_text,
    }


def _resolve_training_queue_row(conn: sqlite3.Connection, queue_task_id: str) -> sqlite3.Row:
    row = conn.execute(
        """
        SELECT
            q.queue_task_id,q.plan_id,q.priority,q.status,q.trainer_match,q.enqueued_at,q.started_at,q.finished_at,
            COALESCE(q.execution_engine,'workflow_native') AS execution_engine,
            COALESCE(q.is_test_data,0) AS queue_is_test_data,
            p.source,p.target_agent_id,p.capability_goal,p.training_tasks_json,p.acceptance_criteria,p.priority AS plan_priority,
            COALESCE(p.is_test_data,0) AS plan_is_test_data,
            COALESCE(p.loop_id,'') AS loop_id,
            a.agent_name
        FROM training_queue q
        INNER JOIN training_plan p ON p.plan_id=q.plan_id
        LEFT JOIN agent_registry a ON a.agent_id=p.target_agent_id
        WHERE q.queue_task_id=?
        LIMIT 1
        """,
        (queue_task_id,),
    ).fetchone()
    if row is None:
        raise TrainingCenterError(
            404,
            "queue task not found",
            "queue_task_not_found",
            {"queue_task_id": queue_task_id},
        )
    return row


def _ensure_plan_loop_id(conn: sqlite3.Connection, row: sqlite3.Row) -> str:
    loop_id = str(row["loop_id"] or "").strip()
    plan_id = str(row["plan_id"] or "").strip()
    if loop_id:
        return loop_id
    if not plan_id:
        return ""
    conn.execute(
        """
        UPDATE training_plan
        SET loop_id=?
        WHERE plan_id=? AND COALESCE(loop_id,'')=''
        """,
        (plan_id, plan_id),
    )
    return plan_id


def _ensure_loop_state_row(
    conn: sqlite3.Connection,
    *,
    loop_id: str,
    seed_row: sqlite3.Row,
    now_text: str,
) -> sqlite3.Row:
    row = conn.execute(
        """
        SELECT
            loop_id,graph_json,current_node_id,metrics_available,metrics_unavailable_reason,is_test_data,created_at,updated_at
        FROM training_loop_state
        WHERE loop_id=?
        LIMIT 1
        """,
        (loop_id,),
    ).fetchone()
    if row is not None:
        return row

    is_test_data = bool(int(seed_row["plan_is_test_data"] or seed_row["queue_is_test_data"] or 0))
    base = _loop_node_base(now_text)
    current = {
        "node_id": str(seed_row["queue_task_id"] or "").strip(),
        "title": "R1 当前",
        "round_index": 1,
        "round_label": "R1",
        "node_type": "round",
        "decision": "等待执行三轮评测",
        "decision_code": "awaiting_evaluation",
        "next_action": "执行三轮评测",
        "next_action_code": "execute",
        "impact": "首轮任务已创建，等待后端回写三轮评测结果",
        "metrics": {
            "avg_score": None,
            "threshold": training_threshold_for_priority(seed_row["priority"]),
            "previous_avg_score": None,
            "run_results": [],
        },
        "metrics_available": False,
        "metrics_unavailable_reason": "evaluation_not_started",
        "queue_task_id": str(seed_row["queue_task_id"] or "").strip(),
        "plan_id": str(seed_row["plan_id"] or "").strip(),
        "status": str(seed_row["status"] or "").strip().lower() or "queued",
        "available_actions": [],
        "run_ids": [],
        "execution_engine": str(seed_row["execution_engine"] or EXECUTION_ENGINE).strip() or EXECUTION_ENGINE,
        "created_at": str(seed_row["enqueued_at"] or "").strip() or now_text,
        "updated_at": now_text,
    }
    graph = {
        "version": 2,
        "loop_id": loop_id,
        "nodes": [base, current],
        "edges": [{"from": base["node_id"], "to": current["node_id"], "kind": "main"}],
        "current_node_id": current["node_id"],
    }
    conn.execute(
        """
        INSERT INTO training_loop_state (
            loop_id,graph_json,current_node_id,metrics_available,metrics_unavailable_reason,is_test_data,created_at,updated_at
        ) VALUES (?,?,?,?,?,?,?,?)
        """,
        (
            loop_id,
            json.dumps(graph, ensure_ascii=False),
            str(current["node_id"] or "").strip(),
            0,
            "evaluation_not_started",
            1 if is_test_data else 0,
            now_text,
            now_text,
        ),
    )
    return conn.execute(
        """
        SELECT
            loop_id,graph_json,current_node_id,metrics_available,metrics_unavailable_reason,is_test_data,created_at,updated_at
        FROM training_loop_state
        WHERE loop_id=?
        LIMIT 1
        """,
        (loop_id,),
    ).fetchone()


def _load_loop_queue_rows(conn: sqlite3.Connection, loop_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            q.queue_task_id,q.plan_id,q.priority,q.status,q.trainer_match,q.enqueued_at,q.started_at,q.finished_at,
            COALESCE(q.execution_engine,'workflow_native') AS execution_engine,
            COALESCE(q.is_test_data,0) AS queue_is_test_data,
            p.source,p.target_agent_id,p.capability_goal,p.training_tasks_json,p.acceptance_criteria,p.created_by,p.created_at AS plan_created_at,
            p.priority AS plan_priority,
            COALESCE(p.is_test_data,0) AS plan_is_test_data,
            COALESCE(p.loop_id,'') AS loop_id,
            a.agent_name,a.lifecycle_state,a.training_gate_state,
            (
                SELECT r.run_id
                FROM training_run r
                WHERE r.queue_task_id=q.queue_task_id
                ORDER BY r.updated_at DESC
                LIMIT 1
            ) AS latest_run_id,
            (
                SELECT r.status
                FROM training_run r
                WHERE r.queue_task_id=q.queue_task_id
                ORDER BY r.updated_at DESC
                LIMIT 1
            ) AS latest_run_status,
            (
                SELECT r.run_ref
                FROM training_run r
                WHERE r.queue_task_id=q.queue_task_id
                ORDER BY r.updated_at DESC
                LIMIT 1
            ) AS latest_run_ref,
            (
                SELECT r.result_summary
                FROM training_run r
                WHERE r.queue_task_id=q.queue_task_id
                ORDER BY r.updated_at DESC
                LIMIT 1
            ) AS latest_result_summary,
            (
                SELECT r.updated_at
                FROM training_run r
                WHERE r.queue_task_id=q.queue_task_id
                ORDER BY r.updated_at DESC
                LIMIT 1
            ) AS latest_run_updated_at
        FROM training_queue q
        INNER JOIN training_plan p ON p.plan_id=q.plan_id
        LEFT JOIN agent_registry a ON a.agent_id=p.target_agent_id
        WHERE COALESCE(p.loop_id,'')=? OR p.plan_id=?
        ORDER BY q.enqueued_at ASC, q.queue_task_id ASC
        """,
        (loop_id, loop_id),
    ).fetchall()


def _load_loop_eval_runs(
    conn: sqlite3.Connection,
    queue_ids: list[str],
) -> dict[str, list[dict[str, Any]]]:
    if not queue_ids:
        return {}
    placeholders = ",".join(["?"] * len(queue_ids))
    rows = conn.execute(
        f"""
        SELECT
            eval_run_id,queue_task_id,round_index,run_index,status,score,evaluation_summary,started_at,finished_at,context_reset,evidence_ref,execution_engine,created_at,updated_at
        FROM training_eval_run
        WHERE queue_task_id IN ({placeholders})
        ORDER BY round_index ASC, queue_task_id ASC, run_index ASC, created_at ASC
        """,
        tuple(queue_ids),
    ).fetchall()
    out: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        qid = str(row["queue_task_id"] or "").strip()
        if not qid:
            continue
        out.setdefault(qid, []).append({name: row[name] for name in row.keys()})
    return out


def _load_queue_audits(
    conn: sqlite3.Connection,
    queue_ids: list[str],
) -> dict[str, list[dict[str, Any]]]:
    if not queue_ids:
        return {}
    placeholders = ",".join(["?"] * len(queue_ids))
    rows = conn.execute(
        f"""
        SELECT audit_id,action,operator,target_id,detail_json,created_at
        FROM training_audit_log
        WHERE target_id IN ({placeholders})
        ORDER BY created_at ASC, audit_id ASC
        """,
        tuple(queue_ids),
    ).fetchall()
    out: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        key = str(row["target_id"] or "").strip()
        if not key:
            continue
        item = {name: row[name] for name in row.keys()}
        item["detail"] = _json_object(row["detail_json"])
        out.setdefault(key, []).append(item)
    return out


def _load_loop_action_audits(conn: sqlite3.Connection, loop_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT audit_id,action,operator,target_id,detail_json,created_at
        FROM training_audit_log
        WHERE target_id=?
          AND action IN ('enter-next-round','rollback-round-increment')
        ORDER BY created_at ASC, audit_id ASC
        """,
        (loop_id,),
    ).fetchall()
    items: list[dict[str, Any]] = []
    for row in rows:
        item = {name: row[name] for name in row.keys()}
        item["detail"] = _json_object(row["detail_json"])
        items.append(item)
    return items


def _round_index_for_queue(
    *,
    order_index: int,
    graph_node: dict[str, Any],
    eval_rows: list[dict[str, Any]],
) -> int:
    for item in eval_rows:
        try:
            ridx = int(item.get("round_index") or 0)
        except Exception:
            ridx = 0
        if ridx > 0:
            return ridx
    try:
        ridx = int(graph_node.get("round_index") or 0)
    except Exception:
        ridx = 0
    if ridx > 0:
        return ridx
    return max(1, int(order_index) + 1)


def _related_action_audits(
    queue_task_id: str,
    *,
    queue_audit_map: dict[str, list[dict[str, Any]]],
    loop_audits: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    items = list(queue_audit_map.get(queue_task_id, []))
    for audit in loop_audits:
        detail = audit.get("detail") if isinstance(audit, dict) else {}
        if not isinstance(detail, dict):
            detail = {}
        if (
            str(detail.get("queue_task_id") or "").strip() == queue_task_id
            or str(detail.get("created_queue_task_id") or "").strip() == queue_task_id
        ):
            items.append(audit)
    items.sort(key=lambda item: (str(item.get("created_at") or ""), str(item.get("audit_id") or "")))
    return items


def _build_workset_changes(
    row: sqlite3.Row,
    *,
    round_index: int,
    previous_tasks: list[str],
    action_audits: list[dict[str, Any]],
    rolled_back: bool,
) -> dict[str, Any]:
    current_tasks = _parse_training_tasks(row["training_tasks_json"])
    added = [task for task in current_tasks if task not in previous_tasks]
    carried = [task for task in current_tasks if task in previous_tasks]
    removed = [task for task in previous_tasks if task not in current_tasks]

    action_reason = ""
    for audit in reversed(action_audits):
        detail = audit.get("detail") if isinstance(audit, dict) else {}
        if not isinstance(detail, dict):
            continue
        action_reason = str(detail.get("reason") or "").strip()
        if action_reason:
            break

    if round_index <= 1:
        delta_summary = f"首轮建立 {len(current_tasks)} 项训练任务工作集"
    elif added or removed:
        parts: list[str] = []
        if added:
            parts.append(f"新增 {len(added)} 项")
        if removed:
            parts.append(f"移除 {len(removed)} 项")
        if carried:
            parts.append(f"保留 {len(carried)} 项")
        delta_summary = "，".join(parts) if parts else "当前轮工作集无结构化变化"
    elif current_tasks:
        delta_summary = f"本轮沿用上轮 {len(carried)} 项训练任务，暂无结构化增删记录"
    else:
        delta_summary = "当前未配置训练任务工作集"

    if rolled_back:
        delta_summary += "；当前轮已执行回退。"
    if action_reason:
        delta_summary += f"；动作说明：{action_reason}"

    items: list[dict[str, Any]] = []
    for task in current_tasks:
        state_key = "added" if task in added or round_index <= 1 else "carried"
        items.append({"kind": "training_task", "label": task, "state": state_key})
    for task in removed:
        items.append({"kind": "training_task", "label": task, "state": "removed"})

    return {
        "queue_task_id": str(row["queue_task_id"] or "").strip(),
        "round_index": round_index,
        "delta_summary": delta_summary,
        "current_items": current_tasks,
        "items": items,
        "added_items": added if round_index > 1 else current_tasks,
        "carried_items": carried,
        "removed_items": removed,
        "rollback_applied": rolled_back,
        "execution_engine": str(row["execution_engine"] or EXECUTION_ENGINE).strip() or EXECUTION_ENGINE,
        "updated_at": str(
            row["latest_run_updated_at"] or row["finished_at"] or row["started_at"] or row["enqueued_at"] or ""
        ).strip(),
    }


def _append_edge(
    edges: list[dict[str, Any]],
    seen: set[tuple[str, str, str]],
    *,
    from_id: str,
    to_id: str,
    kind: str,
    valid_ids: set[str],
) -> None:
    fid = str(from_id or "").strip()
    tid = str(to_id or "").strip()
    edge_kind = str(kind or "main").strip().lower() or "main"
    if not fid or not tid or fid not in valid_ids or tid not in valid_ids:
        return
    key = (fid, tid, edge_kind)
    if key in seen:
        return
    seen.add(key)
    edges.append({"from": fid, "to": tid, "kind": edge_kind})


def _sync_training_loop_read_model(
    conn: sqlite3.Connection,
    *,
    queue_task_id: str,
    now_text: str,
) -> dict[str, Any]:
    seed = _resolve_training_queue_row(conn, queue_task_id)
    loop_id = _ensure_plan_loop_id(conn, seed)
    loop_row = _ensure_loop_state_row(conn, loop_id=loop_id, seed_row=seed, now_text=now_text)
    graph = _parse_loop_graph(loop_row["graph_json"])
    raw_nodes = graph.get("nodes") if isinstance(graph.get("nodes"), list) else []
    raw_edges = graph.get("edges") if isinstance(graph.get("edges"), list) else []
    existing_current_node_id = str(loop_row["current_node_id"] or graph.get("current_node_id") or "").strip()

    graph_nodes_by_id: dict[str, dict[str, Any]] = {}
    rollback_nodes: list[dict[str, Any]] = []
    rollback_targets: set[str] = set()
    for raw_node in raw_nodes:
        if not isinstance(raw_node, dict):
            continue
        node_id = str(raw_node.get("node_id") or "").strip()
        if not node_id:
            continue
        graph_nodes_by_id[node_id] = dict(raw_node)
        if str(raw_node.get("node_type") or "").strip().lower() == "rollback":
            rollback_nodes.append(dict(raw_node))
    for raw_edge in raw_edges:
        if not isinstance(raw_edge, dict):
            continue
        if str(raw_edge.get("kind") or "main").strip().lower() != "rollback":
            continue
        from_id = str(raw_edge.get("from") or raw_edge.get("from_id") or "").strip()
        if from_id:
            rollback_targets.add(from_id)

    queue_rows = _load_loop_queue_rows(conn, loop_id)
    queue_ids = [str(row["queue_task_id"] or "").strip() for row in queue_rows if str(row["queue_task_id"] or "").strip()]
    eval_run_map = _load_loop_eval_runs(conn, queue_ids)
    queue_audit_map = _load_queue_audits(conn, queue_ids)
    loop_audits = _load_loop_action_audits(conn, loop_id)

    base_node = _loop_node_base(str(loop_row["created_at"] or now_text).strip() or now_text)
    nodes: list[dict[str, Any]] = [base_node]
    round_records: list[dict[str, Any]] = []
    history_records: list[dict[str, Any]] = []
    previous_avg_score: float | None = None
    previous_tasks: list[str] = []

    for order_index, row in enumerate(queue_rows):
        qid = str(row["queue_task_id"] or "").strip()
        graph_node = graph_nodes_by_id.get(qid, {})
        eval_rows = eval_run_map.get(qid, [])
        round_index = _round_index_for_queue(
            order_index=order_index,
            graph_node=graph_node,
            eval_rows=eval_rows,
        )
        action_audits = _related_action_audits(
            qid,
            queue_audit_map=queue_audit_map,
            loop_audits=loop_audits,
        )
        rolled_back = qid in rollback_targets
        evaluation = summarize_training_eval_runs(
            priority=row["priority"] or row["plan_priority"],
            run_results=eval_rows,
            previous_avg_score=previous_avg_score,
        )
        if evaluation["metrics_available"] and evaluation["avg_score"] is not None:
            previous_avg_score = float(evaluation["avg_score"])

        workset_changes = _build_workset_changes(
            row,
            round_index=round_index,
            previous_tasks=previous_tasks,
            action_audits=action_audits,
            rolled_back=rolled_back,
        )
        previous_tasks = _parse_training_tasks(row["training_tasks_json"])

        decision = str(evaluation["decision"] or "").strip()
        decision_code = str(evaluation["decision_code"] or "").strip()
        next_action = str(evaluation["next_action"] or "").strip()
        next_action_code = str(evaluation["next_action_code"] or "").strip()
        if not decision:
            queue_status = str(row["status"] or "").strip().lower()
            if not eval_rows:
                decision = "等待执行三轮评测"
                decision_code = "awaiting_evaluation"
                next_action = "执行三轮评测"
                next_action_code = "execute"
            elif queue_status == "running":
                decision = "三轮评测执行中"
                decision_code = "evaluation_running"
                next_action = "等待三轮评测完成"
                next_action_code = ""
            else:
                decision = "三轮评测未完整回写"
                decision_code = "evaluation_partial"
                next_action = "等待三轮评测完成"
                next_action_code = ""

        metrics_payload = {
            "avg_score": evaluation["avg_score"],
            "threshold": evaluation["threshold"],
            "previous_avg_score": evaluation["previous_avg_score"],
            "run_results": evaluation["run_results"],
            "decision_code": decision_code,
            "next_action_code": next_action_code,
        }
        queue_status_value = "rolled_back" if rolled_back else str(row["status"] or "").strip().lower() or "queued"
        title = str(graph_node.get("title") or "").strip() or (
            f"R{round_index}"
            + (
                " 已回退"
                if queue_status_value == "rolled_back"
                else " 当前"
                if queue_status_value not in {"done", "removed"}
                else " 已完成"
            )
        )
        impact = str(graph_node.get("impact") or "").strip() or str(workset_changes["delta_summary"] or "").strip()
        updated_at = str(
            row["latest_run_updated_at"] or row["finished_at"] or row["started_at"] or row["enqueued_at"] or now_text
        ).strip() or now_text
        run_ids = [
            str(item.get("eval_run_id") or "").strip()
            for item in evaluation["run_results"]
            if str(item.get("eval_run_id") or "").strip()
        ]

        node = {
            "node_id": qid,
            "title": title,
            "round_index": round_index,
            "round_label": f"R{round_index}",
            "node_type": "round",
            "decision": decision,
            "decision_code": decision_code,
            "next_action": next_action,
            "next_action_code": next_action_code,
            "impact": impact,
            "metrics": metrics_payload,
            "metrics_available": bool(evaluation["metrics_available"]),
            "metrics_unavailable_reason": str(evaluation["metrics_unavailable_reason"] or "").strip(),
            "queue_task_id": qid,
            "plan_id": str(row["plan_id"] or "").strip(),
            "status": queue_status_value,
            "available_actions": list(evaluation["available_actions"] or []),
            "run_ids": run_ids,
            "execution_engine": str(row["execution_engine"] or EXECUTION_ENGINE).strip() or EXECUTION_ENGINE,
            "created_at": str(row["enqueued_at"] or "").strip() or now_text,
            "updated_at": updated_at,
        }
        nodes.append(node)

        audit_refs = [
            {
                "audit_id": str(item.get("audit_id") or "").strip(),
                "action": str(item.get("action") or "").strip(),
                "created_at": str(item.get("created_at") or "").strip(),
            }
            for item in action_audits
            if str(item.get("audit_id") or "").strip()
        ]
        history_record = {
            "round_index": round_index,
            "queue_task_id": qid,
            "node_id": qid,
            "title": title,
            "decision": decision,
            "decision_code": decision_code,
            "avg_score": evaluation["avg_score"],
            "threshold": evaluation["threshold"],
            "previous_avg_score": evaluation["previous_avg_score"],
            "next_action": next_action,
            "next_action_code": next_action_code,
            "workset_delta_summary": workset_changes["delta_summary"],
            "rollback_applied": rolled_back,
            "audit_refs": audit_refs,
            "created_at": str(row["enqueued_at"] or "").strip() or now_text,
            "updated_at": updated_at,
            "execution_engine": str(row["execution_engine"] or EXECUTION_ENGINE).strip() or EXECUTION_ENGINE,
        }
        history_records.append(history_record)

        round_records.append(
            {
                "queue_task_id": qid,
                "plan_id": str(row["plan_id"] or "").strip(),
                "round_index": round_index,
                "round_label": f"R{round_index}",
                "title": title,
                "status": str(row["status"] or "").strip().lower() or "queued",
                "execution_engine": str(row["execution_engine"] or EXECUTION_ENGINE).strip() or EXECUTION_ENGINE,
                "run_results": evaluation["run_results"],
                "avg_score": evaluation["avg_score"],
                "threshold": evaluation["threshold"],
                "previous_avg_score": evaluation["previous_avg_score"],
                "decision": decision,
                "decision_code": decision_code,
                "next_action": next_action,
                "next_action_code": next_action_code,
                "available_actions": list(evaluation["available_actions"] or []),
                "metrics_available": bool(evaluation["metrics_available"]),
                "metrics_unavailable_reason": str(evaluation["metrics_unavailable_reason"] or "").strip(),
                "workset_changes": workset_changes,
                "history_record": history_record,
                "latest_run_id": str(row["latest_run_id"] or "").strip(),
                "latest_run_status": str(row["latest_run_status"] or "").strip(),
                "latest_run_ref": str(row["latest_run_ref"] or "").strip(),
                "latest_result_summary": str(row["latest_result_summary"] or "").strip(),
                "updated_at": updated_at,
                "created_at": str(row["enqueued_at"] or "").strip() or now_text,
            }
        )

    round_record_by_queue = {
        str(item["queue_task_id"] or "").strip(): item
        for item in round_records
        if str(item["queue_task_id"] or "").strip()
    }
    for raw_node in rollback_nodes:
        parent_qid = str(raw_node.get("queue_task_id") or "").strip()
        round_record = round_record_by_queue.get(parent_qid)
        round_value = int(raw_node.get("round_index") or (round_record.get("round_index") if round_record else 0) or 0)
        nodes.append(
            {
                "node_id": str(raw_node.get("node_id") or "").strip(),
                "title": str(raw_node.get("title") or "撤销本轮新增").strip() or "撤销本轮新增",
                "round_index": round_value,
                "round_label": f"R{round_value}",
                "node_type": "rollback",
                "decision": "已撤销本轮新增",
                "decision_code": "round_increment_rolled_back",
                "next_action": "当前轮已回退",
                "next_action_code": "",
                "impact": str(raw_node.get("impact") or (round_record.get("workset_changes", {}).get("delta_summary") if round_record else "") or "").strip(),
                "metrics": {
                    "avg_score": round_record.get("avg_score") if round_record else None,
                    "threshold": round_record.get("threshold") if round_record else None,
                    "previous_avg_score": round_record.get("previous_avg_score") if round_record else None,
                    "run_results": list(round_record.get("run_results") or []) if round_record else [],
                    "decision_code": str(round_record.get("decision_code") or "").strip() if round_record else "",
                    "next_action_code": str(round_record.get("next_action_code") or "").strip() if round_record else "",
                },
                "metrics_available": bool(round_record.get("metrics_available")) if round_record else False,
                "metrics_unavailable_reason": str(round_record.get("metrics_unavailable_reason") or "").strip() if round_record else "rollback_without_round_metrics",
                "queue_task_id": parent_qid,
                "plan_id": str(raw_node.get("plan_id") or (round_record.get("plan_id") if round_record else "") or "").strip(),
                "status": "active",
                "available_actions": [],
                "run_ids": [
                    str(item.get("eval_run_id") or "").strip()
                    for item in (round_record.get("run_results") or [] if round_record else [])
                    if str(item.get("eval_run_id") or "").strip()
                ],
                "execution_engine": str(
                    raw_node.get("execution_engine")
                    or (round_record.get("execution_engine") if round_record else EXECUTION_ENGINE)
                    or EXECUTION_ENGINE
                ).strip()
                or EXECUTION_ENGINE,
                "created_at": str(raw_node.get("created_at") or now_text).strip() or now_text,
                "updated_at": str(raw_node.get("updated_at") or now_text).strip() or now_text,
            }
        )

    nodes_by_id = {
        str(node.get("node_id") or "").strip(): node
        for node in nodes
        if isinstance(node, dict) and str(node.get("node_id") or "").strip()
    }
    valid_ids = set(nodes_by_id.keys())
    edges: list[dict[str, Any]] = []
    edge_seen: set[tuple[str, str, str]] = set()
    if round_records:
        _append_edge(
            edges,
            edge_seen,
            from_id="baseline",
            to_id=str(round_records[0]["queue_task_id"] or "").strip(),
            kind="main",
            valid_ids=valid_ids,
        )
    for idx in range(1, len(round_records)):
        _append_edge(
            edges,
            edge_seen,
            from_id=str(round_records[idx - 1]["queue_task_id"] or "").strip(),
            to_id=str(round_records[idx]["queue_task_id"] or "").strip(),
            kind="main",
            valid_ids=valid_ids,
        )
    for raw_edge in raw_edges:
        if not isinstance(raw_edge, dict):
            continue
        _append_edge(
            edges,
            edge_seen,
            from_id=str(raw_edge.get("from") or raw_edge.get("from_id") or "").strip(),
            to_id=str(raw_edge.get("to") or raw_edge.get("to_id") or "").strip(),
            kind=str(raw_edge.get("kind") or "main").strip().lower() or "main",
            valid_ids=valid_ids,
        )

    current_node_id = existing_current_node_id if existing_current_node_id in valid_ids else ""
    if not current_node_id:
        current_node_id = str(round_records[-1]["queue_task_id"] or "").strip() if round_records else "baseline"
    current_node = nodes_by_id.get(current_node_id) or base_node

    queue_row_map = {
        str(row["queue_task_id"] or "").strip(): row
        for row in queue_rows
        if str(row["queue_task_id"] or "").strip()
    }
    selected_round = round_record_by_queue.get(queue_task_id)
    selected_row = queue_row_map.get(queue_task_id, seed)
    selected_workset = dict(selected_round.get("workset_changes") or {}) if isinstance(selected_round, dict) else {
        "queue_task_id": queue_task_id,
        "round_index": 0,
        "delta_summary": "当前没有可用工作集摘要",
        "current_items": _parse_training_tasks(selected_row["training_tasks_json"]),
        "items": [],
        "added_items": [],
        "carried_items": [],
        "removed_items": [],
        "rollback_applied": False,
        "execution_engine": str(selected_row["execution_engine"] or EXECUTION_ENGINE).strip() or EXECUTION_ENGINE,
        "updated_at": now_text,
    }
    overview_decision = str(selected_round.get("decision") or "").strip() if isinstance(selected_round, dict) else "等待执行三轮评测"
    overview_decision_code = str(selected_round.get("decision_code") or "").strip() if isinstance(selected_round, dict) else "awaiting_evaluation"
    overview_next_action = str(selected_round.get("next_action") or "").strip() if isinstance(selected_round, dict) else "执行三轮评测"
    overview_next_action_code = str(selected_round.get("next_action_code") or "").strip() if isinstance(selected_round, dict) else "execute"
    overview_available_actions = list(selected_round.get("available_actions") or []) if isinstance(selected_round, dict) else []
    if (
        selected_workset.get("rollback_applied")
        and str(current_node.get("node_type") or "").strip().lower() == "rollback"
        and str(current_node.get("queue_task_id") or "").strip() == queue_task_id
    ):
        overview_decision = "本轮已回退"
        overview_decision_code = "round_increment_rolled_back"
        overview_next_action = "当前轮已回退"
        overview_next_action_code = ""
        overview_available_actions = []
    current_overview = {
        "queue_task_id": queue_task_id,
        "plan_id": str(selected_row["plan_id"] or "").strip(),
        "loop_id": loop_id,
        "current_node_id": current_node_id,
        "selected_node_id": queue_task_id,
        "target_agent_id": str(selected_row["target_agent_id"] or "").strip(),
        "agent_name": str(selected_row["agent_name"] or selected_row["target_agent_id"] or "").strip(),
        "capability_goal": str(selected_row["capability_goal"] or "").strip(),
        "acceptance_criteria": str(selected_row["acceptance_criteria"] or "").strip(),
        "priority": str(selected_row["priority"] or selected_row["plan_priority"] or "").strip() or "P1",
        "queue_status": str(selected_row["status"] or "").strip().lower() or "queued",
        "execution_engine": str(selected_row["execution_engine"] or EXECUTION_ENGINE).strip() or EXECUTION_ENGINE,
        "round_index": int(selected_round.get("round_index") or 0) if isinstance(selected_round, dict) else 0,
        "avg_score": selected_round.get("avg_score") if isinstance(selected_round, dict) else None,
        "threshold": selected_round.get("threshold") if isinstance(selected_round, dict) else training_threshold_for_priority(selected_row["priority"]),
        "previous_avg_score": selected_round.get("previous_avg_score") if isinstance(selected_round, dict) else None,
        "decision": overview_decision,
        "decision_code": overview_decision_code,
        "next_action": overview_next_action,
        "next_action_code": overview_next_action_code,
        "metrics_available": bool(selected_round.get("metrics_available")) if isinstance(selected_round, dict) else False,
        "metrics_unavailable_reason": str(selected_round.get("metrics_unavailable_reason") or "").strip() if isinstance(selected_round, dict) else "evaluation_not_started",
        "available_actions": overview_available_actions,
        "latest_run_id": str(selected_round.get("latest_run_id") or "").strip() if isinstance(selected_round, dict) else str(selected_row["latest_run_id"] or "").strip(),
        "latest_run_status": str(selected_round.get("latest_run_status") or "").strip() if isinstance(selected_round, dict) else str(selected_row["latest_run_status"] or "").strip(),
        "latest_run_ref": str(selected_round.get("latest_run_ref") or "").strip() if isinstance(selected_round, dict) else str(selected_row["latest_run_ref"] or "").strip(),
        "latest_result_summary": str(selected_round.get("latest_result_summary") or "").strip() if isinstance(selected_round, dict) else str(selected_row["latest_result_summary"] or "").strip(),
        "updated_at": str(selected_round.get("updated_at") or now_text).strip() if isinstance(selected_round, dict) else now_text,
    }

    synced_graph = {
        "version": 2,
        "loop_id": loop_id,
        "nodes": nodes,
        "edges": edges,
        "current_node_id": current_node_id,
    }
    conn.execute(
        """
        UPDATE training_loop_state
        SET graph_json=?,
            current_node_id=?,
            metrics_available=?,
            metrics_unavailable_reason=?,
            updated_at=?
        WHERE loop_id=?
        """,
        (
            json.dumps(synced_graph, ensure_ascii=False),
            current_node_id,
            1 if bool(current_node.get("metrics_available")) else 0,
            str(current_node.get("metrics_unavailable_reason") or "").strip(),
            now_text,
            loop_id,
        ),
    )

    return {
        "loop_id": loop_id,
        "is_test_data": bool(int(loop_row["is_test_data"] or 0)),
        "queue_task_id": queue_task_id,
        "nodes": nodes,
        "edges": edges,
        "nodes_by_id": nodes_by_id,
        "current_node_id": current_node_id,
        "current_node": current_node,
        "queue_rows": queue_rows,
        "queue_row_map": queue_row_map,
        "round_records": round_records,
        "round_record_by_queue": round_record_by_queue,
        "history_records": history_records,
        "current_overview": current_overview,
        "workset_changes": selected_workset,
        "evaluations": round_records,
        "metrics_available": bool(current_node.get("metrics_available")),
        "metrics_unavailable_reason": str(current_node.get("metrics_unavailable_reason") or "").strip(),
        "graph": synced_graph,
    }


def get_training_queue_loop(
    root: Path,
    queue_task_id_text: str,
    *,
    include_test_data: bool = True,
) -> dict[str, object]:
    qid = safe_token(str(queue_task_id_text or ""), "", 160)
    if not qid:
        raise TrainingCenterError(400, "queue_task_id required", "queue_task_id_required")

    conn = connect_db(root)
    try:
        read_model = _sync_training_loop_read_model(
            conn,
            queue_task_id=qid,
            now_text=iso_ts(now_local()),
        )
        conn.commit()
    finally:
        conn.close()

    if bool(read_model["is_test_data"]) and not include_test_data:
        raise TrainingCenterError(
            404,
            "test data hidden when include_test_data=false",
            "test_data_hidden",
            {"queue_task_id": qid, "loop_id": str(read_model["loop_id"] or "")},
        )

    return {
        "loop_id": str(read_model["loop_id"] or ""),
        "queue_task_id": qid,
        "current_node_id": str(read_model["current_node_id"] or ""),
        "nodes": list(read_model["nodes"] or []),
        "edges": list(read_model["edges"] or []),
        "metrics_available": bool(read_model["metrics_available"]),
        "metrics_unavailable_reason": str(read_model["metrics_unavailable_reason"] or ""),
        "is_test_data": bool(read_model["is_test_data"]),
    }


def get_training_queue_status_detail(
    root: Path,
    queue_task_id_text: str,
    *,
    include_test_data: bool = True,
) -> dict[str, object]:
    qid = safe_token(str(queue_task_id_text or ""), "", 160)
    if not qid:
        raise TrainingCenterError(400, "queue_task_id required", "queue_task_id_required")

    conn = connect_db(root)
    try:
        read_model = _sync_training_loop_read_model(
            conn,
            queue_task_id=qid,
            now_text=iso_ts(now_local()),
        )
        conn.commit()
    finally:
        conn.close()

    if bool(read_model["is_test_data"]) and not include_test_data:
        raise TrainingCenterError(
            404,
            "test data hidden when include_test_data=false",
            "test_data_hidden",
            {"queue_task_id": qid, "loop_id": str(read_model["loop_id"] or "")},
        )

    return {
        "queue_task_id": qid,
        "loop_id": str(read_model["loop_id"] or ""),
        "current_node_id": str(read_model["current_node_id"] or ""),
        "execution_engine": EXECUTION_ENGINE,
        "current_overview": dict(read_model["current_overview"] or {}),
        "workset_changes": dict(read_model["workset_changes"] or {}),
        "evaluations": list(read_model["evaluations"] or []),
        "history_records": list(read_model["history_records"] or []),
        "is_test_data": bool(read_model["is_test_data"]),
    }


def enter_training_queue_next_round(
    root: Path,
    *,
    queue_task_id_text: str,
    operator: str,
    reason: str = "",
) -> dict[str, object]:
    qid = safe_token(str(queue_task_id_text or ""), "", 160)
    if not qid:
        raise TrainingCenterError(400, "queue_task_id required", "queue_task_id_required")
    operator_text = safe_token(str(operator or "web-user"), "web-user", 80)
    reason_text = str(reason or "").strip()

    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        read_model = _sync_training_loop_read_model(
            conn,
            queue_task_id=qid,
            now_text=iso_ts(now_local()),
        )
        current_node_id = str(read_model["current_node_id"] or "").strip()
        current_node = read_model["nodes_by_id"].get(current_node_id) if isinstance(read_model.get("nodes_by_id"), dict) else None
        if not current_node or str(current_node.get("queue_task_id") or current_node.get("node_id") or "").strip() != qid:
            raise TrainingCenterError(
                409,
                "loop current node changed",
                "loop_current_task_changed",
                {"queue_task_id": qid, "loop_id": str(read_model["loop_id"] or ""), "current_node_id": current_node_id},
            )
        if str(current_node.get("node_type") or "").strip().lower() != "round":
            raise TrainingCenterError(
                409,
                "current node is not round",
                "loop_current_node_not_round",
                {"queue_task_id": qid, "current_node_id": current_node_id},
            )
        available_actions = list(current_node.get("available_actions") or [])
        if "enter-next-round" not in available_actions:
            raise TrainingCenterError(
                409,
                "enter next round not available",
                "enter_next_round_not_available",
                {
                    "queue_task_id": qid,
                    "available_actions": available_actions,
                    "decision": str(current_node.get("decision") or "").strip(),
                    "decision_code": str(current_node.get("decision_code") or "").strip(),
                },
            )

        graph = _parse_loop_graph(read_model["graph"])
        raw_edges = graph.get("edges") if isinstance(graph.get("edges"), list) else []
        for raw_edge in raw_edges:
            if not isinstance(raw_edge, dict):
                continue
            if str(raw_edge.get("kind") or "main").strip().lower() == "rollback":
                continue
            if str(raw_edge.get("from") or raw_edge.get("from_id") or "").strip() != qid:
                continue
            existing_next_qid = str(raw_edge.get("to") or raw_edge.get("to_id") or "").strip()
            if existing_next_qid:
                raise TrainingCenterError(
                    409,
                    "next round already exists",
                    "loop_next_round_exists",
                    {
                        "queue_task_id": qid,
                        "loop_id": str(read_model["loop_id"] or ""),
                        "created_queue_task_id": existing_next_qid,
                    },
                )

        seed = _resolve_training_queue_row(conn, qid)
        loop_id = _ensure_plan_loop_id(conn, seed)
        now_text = iso_ts(now_local())
        plan_id_text = training_plan_id()
        next_queue_task_id = training_queue_task_id()
        priority = str(seed["priority"] or seed["plan_priority"] or "").strip() or "P1"
        execution_engine = EXECUTION_ENGINE
        trainer_match = str(seed["trainer_match"] or "").strip()
        is_test_data = bool(int(seed["plan_is_test_data"] or seed["queue_is_test_data"] or 0))
        next_round_index = int(current_node.get("round_index") or 0) + 1

        conn.execute(
            """
            INSERT INTO training_plan (
                plan_id,loop_id,source,target_agent_id,capability_goal,training_tasks_json,acceptance_criteria,priority,similar_flag,created_by,is_test_data,created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                plan_id_text,
                loop_id,
                "loop",
                str(seed["target_agent_id"] or "").strip(),
                str(seed["capability_goal"] or "").strip(),
                str(seed["training_tasks_json"] or "[]"),
                str(seed["acceptance_criteria"] or "").strip(),
                priority,
                0,
                operator_text,
                1 if is_test_data else 0,
                now_text,
            ),
        )
        conn.execute(
            """
            INSERT INTO training_queue (
                queue_task_id,plan_id,priority,status,execution_engine,trainer_match,is_test_data,enqueued_at,started_at,finished_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (
                next_queue_task_id,
                plan_id_text,
                priority,
                "queued",
                execution_engine,
                trainer_match,
                1 if is_test_data else 0,
                now_text,
                "",
                "",
            ),
        )

        nodes = list(graph.get("nodes") or [])
        if not any(str(node.get("node_id") or "").strip() == next_queue_task_id for node in nodes if isinstance(node, dict)):
            current_metrics = current_node.get("metrics") if isinstance(current_node.get("metrics"), dict) else {}
            nodes.append(
                {
                    "node_id": next_queue_task_id,
                    "title": f"R{next_round_index} 当前",
                    "round_index": next_round_index,
                    "round_label": f"R{next_round_index}",
                    "node_type": "round",
                    "decision": "等待执行三轮评测",
                    "decision_code": "awaiting_evaluation",
                    "next_action": "执行三轮评测",
                    "next_action_code": "execute",
                    "impact": reason_text or f"由 R{int(current_node.get('round_index') or 0)} 推进到下一轮",
                    "metrics": {
                        "avg_score": None,
                        "threshold": training_threshold_for_priority(priority),
                        "previous_avg_score": _safe_float(current_metrics.get("avg_score")),
                        "run_results": [],
                    },
                    "metrics_available": False,
                    "metrics_unavailable_reason": "evaluation_not_started",
                    "queue_task_id": next_queue_task_id,
                    "plan_id": plan_id_text,
                    "status": "queued",
                    "available_actions": [],
                    "run_ids": [],
                    "execution_engine": execution_engine,
                    "created_at": now_text,
                    "updated_at": now_text,
                }
            )
        edges = list(graph.get("edges") or [])
        edges.append({"from": qid, "to": next_queue_task_id, "kind": "main"})
        graph["nodes"] = nodes
        graph["edges"] = edges
        graph["current_node_id"] = next_queue_task_id

        conn.execute(
            """
            UPDATE training_loop_state
            SET graph_json=?,
                current_node_id=?,
                metrics_available=0,
                metrics_unavailable_reason='evaluation_not_started',
                updated_at=?
            WHERE loop_id=?
            """,
            (
                json.dumps(graph, ensure_ascii=False),
                next_queue_task_id,
                now_text,
                loop_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    audit_id = append_training_center_audit(
        root,
        action="enter-next-round",
        operator=operator_text,
        target_id=loop_id,
        detail={
            "queue_task_id": qid,
            "loop_id": loop_id,
            "created_queue_task_id": next_queue_task_id,
            "created_plan_id": plan_id_text,
            "reason": reason_text,
            "execution_engine": EXECUTION_ENGINE,
        },
    )
    return {
        "ok": True,
        "audit_id": audit_id,
        "loop_id": loop_id,
        "current_node_id": next_queue_task_id,
        "created_queue_task_id": next_queue_task_id,
        "created_plan_id": plan_id_text,
        "execution_engine": EXECUTION_ENGINE,
    }


def rollback_training_queue_round_increment(
    root: Path,
    *,
    queue_task_id_text: str,
    operator: str,
    reason: str = "",
) -> dict[str, object]:
    qid = safe_token(str(queue_task_id_text or ""), "", 160)
    if not qid:
        raise TrainingCenterError(400, "queue_task_id required", "queue_task_id_required")
    operator_text = safe_token(str(operator or "web-user"), "web-user", 80)
    reason_text = str(reason or "").strip()

    conn = connect_db(root)
    try:
        conn.execute("BEGIN IMMEDIATE")
        read_model = _sync_training_loop_read_model(
            conn,
            queue_task_id=qid,
            now_text=iso_ts(now_local()),
        )
        current_node_id = str(read_model["current_node_id"] or "").strip()
        current_node = read_model["nodes_by_id"].get(current_node_id) if isinstance(read_model.get("nodes_by_id"), dict) else None
        if not current_node or str(current_node.get("queue_task_id") or current_node.get("node_id") or "").strip() != qid:
            raise TrainingCenterError(
                409,
                "loop current node changed",
                "loop_current_task_changed",
                {"queue_task_id": qid, "loop_id": str(read_model["loop_id"] or ""), "current_node_id": current_node_id},
            )
        if str(current_node.get("node_type") or "").strip().lower() != "round":
            raise TrainingCenterError(
                409,
                "current node is not round",
                "loop_current_node_not_round",
                {"queue_task_id": qid, "current_node_id": current_node_id},
            )
        available_actions = list(current_node.get("available_actions") or [])
        if "rollback-round-increment" not in available_actions:
            raise TrainingCenterError(
                409,
                "rollback not available",
                "rollback_round_increment_not_available",
                {
                    "queue_task_id": qid,
                    "available_actions": available_actions,
                    "decision": str(current_node.get("decision") or "").strip(),
                    "decision_code": str(current_node.get("decision_code") or "").strip(),
                },
            )

        loop_id = str(read_model["loop_id"] or "").strip()
        graph = _parse_loop_graph(read_model["graph"])
        raw_edges = graph.get("edges") if isinstance(graph.get("edges"), list) else []
        rollback_node_id = f"rb-{qid}"
        for raw_edge in raw_edges:
            if not isinstance(raw_edge, dict):
                continue
            if str(raw_edge.get("kind") or "main").strip().lower() != "rollback":
                continue
            if str(raw_edge.get("from") or raw_edge.get("from_id") or "").strip() != qid:
                continue
            existing_rb = str(raw_edge.get("to") or raw_edge.get("to_id") or "").strip()
            if existing_rb:
                raise TrainingCenterError(
                    409,
                    "rollback already exists",
                    "loop_rollback_exists",
                    {"queue_task_id": qid, "loop_id": loop_id, "rollback_node_id": existing_rb},
                )

        now_text = iso_ts(now_local())
        nodes = list(graph.get("nodes") or [])
        if not any(str(node.get("node_id") or "").strip() == rollback_node_id for node in nodes if isinstance(node, dict)):
            metrics_payload = current_node.get("metrics") if isinstance(current_node.get("metrics"), dict) else {
                "avg_score": None,
                "threshold": None,
                "previous_avg_score": None,
                "run_results": [],
            }
            nodes.append(
                {
                    "node_id": rollback_node_id,
                    "title": "撤销本轮新增",
                    "round_index": int(current_node.get("round_index") or 0),
                    "round_label": f"R{int(current_node.get('round_index') or 0)}",
                    "node_type": "rollback",
                    "decision": "已撤销本轮新增",
                    "decision_code": "round_increment_rolled_back",
                    "next_action": "当前轮已回退",
                    "next_action_code": "",
                    "impact": reason_text or f"按当前轮判定回退 R{int(current_node.get('round_index') or 0)} 的本轮新增",
                    "metrics": metrics_payload,
                    "metrics_available": bool(current_node.get("metrics_available")),
                    "metrics_unavailable_reason": str(current_node.get("metrics_unavailable_reason") or "").strip(),
                    "queue_task_id": qid,
                    "plan_id": str(current_node.get("plan_id") or "").strip(),
                    "status": "active",
                    "available_actions": [],
                    "run_ids": list(current_node.get("run_ids") or []),
                    "execution_engine": str(current_node.get("execution_engine") or EXECUTION_ENGINE).strip() or EXECUTION_ENGINE,
                    "created_at": now_text,
                    "updated_at": now_text,
                }
            )
        edges = list(graph.get("edges") or [])
        edges.append({"from": qid, "to": rollback_node_id, "kind": "rollback"})
        graph["nodes"] = nodes
        graph["edges"] = edges
        graph["current_node_id"] = rollback_node_id

        conn.execute(
            """
            UPDATE training_loop_state
            SET graph_json=?,
                current_node_id=?,
                metrics_available=?,
                metrics_unavailable_reason=?,
                updated_at=?
            WHERE loop_id=?
            """,
            (
                json.dumps(graph, ensure_ascii=False),
                rollback_node_id,
                1 if bool(current_node.get("metrics_available")) else 0,
                str(current_node.get("metrics_unavailable_reason") or "").strip(),
                now_text,
                loop_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    audit_id = append_training_center_audit(
        root,
        action="rollback-round-increment",
        operator=operator_text,
        target_id=loop_id,
        detail={
            "queue_task_id": qid,
            "loop_id": loop_id,
            "rollback_node_id": rollback_node_id,
            "reason": reason_text,
            "execution_engine": EXECUTION_ENGINE,
        },
    )
    return {
        "ok": True,
        "audit_id": audit_id,
        "loop_id": loop_id,
        "current_node_id": rollback_node_id,
        "rollback_node_id": rollback_node_id,
        "execution_engine": EXECUTION_ENGINE,
    }
