from __future__ import annotations


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


def _parse_loop_graph(raw: object) -> dict:
    if isinstance(raw, dict):
        return dict(raw)
    if not raw:
        return {}
    try:
        payload = json.loads(str(raw))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _loop_node_base(now_text: str) -> dict:
    return {
        "node_id": "baseline",
        "title": "基线",
        "round_index": 0,
        "node_type": "baseline",
        "decision": "暂无历史",
        "next_action": "执行首轮评测",
        "impact": "",
        "metrics": None,
        "metrics_available": False,
        "queue_task_id": "",
        "plan_id": "",
        "status": "active",
        "created_at": now_text,
        "updated_at": now_text,
    }


def _loop_node_for_queue(
    *,
    queue_task_id: str,
    plan_id: str,
    status: str,
    enqueued_at: str,
    now_text: str,
    round_index: int,
) -> dict:
    qid = str(queue_task_id or "").strip()
    status = str(status or "").strip() or "queued"
    title = f"R{max(1, int(round_index))}"
    if status.lower() not in {"done", "failed", "removed"}:
        title += " 当前"
    else:
        title += " 已结束"
    return {
        "node_id": qid,
        "title": title,
        "round_index": int(round_index) if round_index else 1,
        "node_type": "round",
        "decision": status,
        "next_action": "enter-next-round / rollback-round-increment",
        "impact": "",
        "metrics": None,
        "metrics_available": False,
        "queue_task_id": qid,
        "plan_id": str(plan_id or "").strip(),
        "status": "active",
        "created_at": str(enqueued_at or "").strip() or now_text,
        "updated_at": now_text,
    }


def _graph_next_round_index(nodes: list[dict]) -> int:
    idx = 0
    for node in nodes:
        try:
            ridx = int(node.get("round_index") or 0)
        except Exception:
            ridx = 0
        idx = max(idx, ridx)
    return idx + 1 if idx >= 1 else 2


def _resolve_training_queue_row(conn: sqlite3.Connection, queue_task_id: str) -> sqlite3.Row:
    row = conn.execute(
        """
        SELECT
            q.queue_task_id,q.plan_id,q.priority,q.status,q.trainer_match,q.enqueued_at,q.started_at,q.finished_at,
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
    current = _loop_node_for_queue(
        queue_task_id=str(seed_row["queue_task_id"] or "").strip(),
        plan_id=str(seed_row["plan_id"] or "").strip(),
        status=str(seed_row["status"] or "").strip(),
        enqueued_at=str(seed_row["enqueued_at"] or "").strip(),
        now_text=now_text,
        round_index=1,
    )
    graph = {
        "version": 1,
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
            "scoring_not_integrated",
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
        seed = _resolve_training_queue_row(conn, qid)
        loop_id = _ensure_plan_loop_id(conn, seed)
        now_text = iso_ts(now_local())
        loop_row = _ensure_loop_state_row(conn, loop_id=loop_id, seed_row=seed, now_text=now_text)
        conn.commit()
    finally:
        conn.close()

    is_test_data = bool(int(loop_row["is_test_data"] or 0))
    if is_test_data and not include_test_data:
        raise TrainingCenterError(
            404,
            "test data hidden when include_test_data=false",
            "test_data_hidden",
            {"queue_task_id": qid, "loop_id": loop_id},
        )

    graph = _parse_loop_graph(loop_row["graph_json"])
    nodes = graph.get("nodes") if isinstance(graph.get("nodes"), list) else []
    edges = graph.get("edges") if isinstance(graph.get("edges"), list) else []
    current_node_id = str(loop_row["current_node_id"] or graph.get("current_node_id") or "").strip()

    nodes_by_id: dict[str, dict] = {}
    for item in nodes:
        if isinstance(item, dict):
            nid = str(item.get("node_id") or "").strip()
            if nid:
                nodes_by_id[nid] = item
    if current_node_id and current_node_id not in nodes_by_id:
        current_node_id = ""
    if not current_node_id and qid in nodes_by_id:
        current_node_id = qid
    if not current_node_id and nodes_by_id:
        # best-effort: latest round_index
        selected = None
        best = -1
        for node in nodes_by_id.values():
            try:
                ridx = int(node.get("round_index") or 0)
            except Exception:
                ridx = 0
            if ridx >= best:
                best = ridx
                selected = node
        current_node_id = str(selected.get("node_id") if isinstance(selected, dict) else "") if selected else ""

    return {
        "loop_id": str(loop_row["loop_id"] or loop_id),
        "queue_task_id": qid,
        "current_node_id": current_node_id,
        "nodes": nodes,
        "edges": edges,
        "metrics_available": bool(int(loop_row["metrics_available"] or 0)),
        "metrics_unavailable_reason": str(loop_row["metrics_unavailable_reason"] or "").strip(),
        "is_test_data": is_test_data,
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
        seed = _resolve_training_queue_row(conn, qid)
        loop_id = _ensure_plan_loop_id(conn, seed)
        now_text = iso_ts(now_local())
        loop_row = _ensure_loop_state_row(conn, loop_id=loop_id, seed_row=seed, now_text=now_text)

        graph = _parse_loop_graph(loop_row["graph_json"])
        nodes = graph.get("nodes") if isinstance(graph.get("nodes"), list) else []
        edges = graph.get("edges") if isinstance(graph.get("edges"), list) else []
        current_node_id = str(loop_row["current_node_id"] or graph.get("current_node_id") or "").strip()
        nodes_by_id = {str(n.get("node_id") or ""): n for n in nodes if isinstance(n, dict) and str(n.get("node_id") or "")}
        current_node = nodes_by_id.get(current_node_id) if current_node_id else None

        if not current_node or str(current_node.get("queue_task_id") or current_node.get("node_id") or "").strip() != qid:
            raise TrainingCenterError(
                409,
                "loop current node changed",
                "loop_current_task_changed",
                {"queue_task_id": qid, "loop_id": loop_id, "current_node_id": current_node_id},
            )

        # Create a new plan + queue item for the next round, keeping loop_id stable.
        plan_id_text = training_plan_id()
        next_queue_task_id = training_queue_task_id()
        target_agent_id = str(seed["target_agent_id"] or "").strip()
        capability_goal = str(seed["capability_goal"] or "").strip()
        training_tasks_json = str(seed["training_tasks_json"] or "[]")
        acceptance_criteria = str(seed["acceptance_criteria"] or "").strip()
        priority = str(seed["priority"] or seed["plan_priority"] or "").strip() or "P1"
        execution_engine = "workflow_native"
        trainer_match = str(seed["trainer_match"] or "").strip()
        is_test_data = bool(int(seed["plan_is_test_data"] or seed["queue_is_test_data"] or 0))

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
                target_agent_id,
                capability_goal,
                training_tasks_json,
                acceptance_criteria,
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

        next_round_index = _graph_next_round_index(nodes)
        next_node = _loop_node_for_queue(
            queue_task_id=next_queue_task_id,
            plan_id=plan_id_text,
            status="queued",
            enqueued_at=now_text,
            now_text=now_text,
            round_index=next_round_index,
        )
        next_node["impact"] = reason_text
        nodes.append(next_node)
        edges.append({"from": str(current_node.get("node_id") or qid), "to": next_queue_task_id, "kind": "main"})
        graph["nodes"] = nodes
        graph["edges"] = edges
        graph["current_node_id"] = next_queue_task_id

        conn.execute(
            """
            UPDATE training_loop_state
            SET graph_json=?,
                current_node_id=?,
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
        },
    )
    return {
        "ok": True,
        "audit_id": audit_id,
        "loop_id": loop_id,
        "current_node_id": next_queue_task_id,
        "created_queue_task_id": next_queue_task_id,
        "created_plan_id": plan_id_text,
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
        seed = _resolve_training_queue_row(conn, qid)
        loop_id = _ensure_plan_loop_id(conn, seed)
        now_text = iso_ts(now_local())
        loop_row = _ensure_loop_state_row(conn, loop_id=loop_id, seed_row=seed, now_text=now_text)

        graph = _parse_loop_graph(loop_row["graph_json"])
        nodes = graph.get("nodes") if isinstance(graph.get("nodes"), list) else []
        edges = graph.get("edges") if isinstance(graph.get("edges"), list) else []
        current_node_id = str(loop_row["current_node_id"] or graph.get("current_node_id") or "").strip()
        nodes_by_id = {str(n.get("node_id") or ""): n for n in nodes if isinstance(n, dict) and str(n.get("node_id") or "")}
        current_node = nodes_by_id.get(current_node_id) if current_node_id else None

        if not current_node or str(current_node.get("queue_task_id") or current_node.get("node_id") or "").strip() != qid:
            raise TrainingCenterError(
                409,
                "loop current node changed",
                "loop_current_task_changed",
                {"queue_task_id": qid, "loop_id": loop_id, "current_node_id": current_node_id},
            )

        if str(current_node.get("node_type") or "").strip().lower() == "rollback":
            raise TrainingCenterError(
                409,
                "already rolled back",
                "loop_already_rolled_back",
                {"queue_task_id": qid, "loop_id": loop_id, "current_node_id": current_node_id},
            )

        rollback_node_id = f"rb-{qid}"
        if rollback_node_id in nodes_by_id:
            raise TrainingCenterError(
                409,
                "rollback already exists",
                "loop_rollback_exists",
                {"queue_task_id": qid, "loop_id": loop_id, "rollback_node_id": rollback_node_id},
            )

        try:
            round_index = int(current_node.get("round_index") or 0)
        except Exception:
            round_index = 0
        rb = {
            "node_id": rollback_node_id,
            "title": "回退本轮新增",
            "round_index": round_index,
            "node_type": "rollback",
            "decision": "rollback-round-increment",
            "next_action": "enter-next-round / execute-eval",
            "impact": reason_text,
            "metrics": None,
            "metrics_available": False,
            "queue_task_id": qid,
            "plan_id": str(current_node.get("plan_id") or "").strip(),
            "status": "active",
            "created_at": now_text,
            "updated_at": now_text,
        }
        current_node["status"] = "rolled_back"
        current_node["updated_at"] = now_text
        nodes.append(rb)
        edges.append({"from": str(current_node.get("node_id") or qid), "to": rollback_node_id, "kind": "rollback"})
        graph["nodes"] = nodes
        graph["edges"] = edges
        graph["current_node_id"] = rollback_node_id

        conn.execute(
            """
            UPDATE training_loop_state
            SET graph_json=?,
                current_node_id=?,
                updated_at=?
            WHERE loop_id=?
            """,
            (
                json.dumps(graph, ensure_ascii=False),
                rollback_node_id,
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
        },
    )
    return {
        "ok": True,
        "audit_id": audit_id,
        "loop_id": loop_id,
        "current_node_id": rollback_node_id,
        "rollback_node_id": rollback_node_id,
    }
