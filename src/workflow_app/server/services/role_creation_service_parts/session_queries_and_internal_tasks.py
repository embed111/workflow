def list_role_creation_sessions(root: Path) -> dict[str, Any]:
    _ensure_role_creation_tables(root)
    conn = connect_db(root)
    try:
        rows = conn.execute(
            "SELECT * FROM role_creation_sessions ORDER BY updated_at DESC,created_at DESC,session_id DESC"
        ).fetchall()
    finally:
        conn.close()
    items = [_session_row_to_summary(row) for row in rows]
    return {"items": items, "total": len(items)}


def get_role_creation_session_detail(root: Path, session_id: str) -> dict[str, Any]:
    _ensure_role_creation_tables(root)
    session_key = safe_token(str(session_id or ""), "", 160)
    if not session_key:
        raise TrainingCenterError(400, "session_id required", "role_creation_session_id_required")
    conn = connect_db(root)
    try:
        row = _fetch_session_row(conn, session_key)
        session_summary = _session_row_to_summary(row)
        messages = _list_session_messages(conn, session_key)
        task_refs = _list_task_refs(conn, session_key)
    finally:
        conn.close()
    role_spec, missing_fields = _build_role_spec(messages)
    assignment_graph = {}
    if session_summary.get("assignment_ticket_id"):
        try:
            assignment_graph = assignment_service.get_assignment_graph(
                root,
                session_summary["assignment_ticket_id"],
                active_loaded=400,
                active_batch_size=200,
                history_loaded=400,
                history_batch_size=50,
                include_test_data=True,
            )
        except Exception:
            assignment_graph = {}
    stages, stage_meta = _project_stages(session_summary, task_refs=task_refs, assignment_graph=assignment_graph)
    current_stage_key = str(stage_meta.get("current_stage_key") or session_summary.get("current_stage_key") or "persona_collection")
    current_stage_index = int(stage_meta.get("current_stage_index") or session_summary.get("current_stage_index") or 2)
    needs_sync = (
        _json_dumps(role_spec) != str(row["role_spec_json"] or "{}")
        or _json_dumps(missing_fields) != str(row["missing_fields_json"] or "[]")
        or _role_creation_title_from_spec(role_spec, session_summary.get("session_title") or "") != session_summary.get("session_title")
    )
    if needs_sync and session_summary.get("status") != "completed":
        conn = connect_db(root)
        try:
            conn.execute(
                """
                UPDATE role_creation_sessions
                SET session_title=?,role_spec_json=?,missing_fields_json=?,updated_at=?
                WHERE session_id=?
                """,
                (
                    _role_creation_title_from_spec(role_spec, session_summary.get("session_title") or ""),
                    _json_dumps(role_spec),
                    _json_dumps(missing_fields),
                    _tc_now_text(),
                    session_key,
                ),
            )
            conn.commit()
        finally:
            conn.close()
        session_summary["session_title"] = _role_creation_title_from_spec(role_spec, session_summary.get("session_title") or "")
        session_summary["missing_fields"] = list(missing_fields)
    created_agent = _current_agent_runtime_payload(root, session_summary.get("created_agent_id") or "")
    return {
        "session": {
            **session_summary,
            "current_stage_key": current_stage_key,
            "current_stage_index": current_stage_index,
            "current_stage_title": str(stage_meta.get("current_stage_title") or ""),
        },
        "messages": messages,
        "role_spec": role_spec,
        "profile": _role_profile_payload(role_spec, missing_fields, session_summary),
        "stages": stages,
        "stage_meta": stage_meta,
        "task_refs": task_refs,
        "assignment_graph": assignment_graph,
        "created_agent": created_agent,
    }


def _raise_role_creation_assignment_error(exc: BaseException, default_code: str) -> None:
    if isinstance(exc, TrainingCenterError):
        raise exc
    status_code = int(getattr(exc, "status_code", 500) or 500)
    code = str(getattr(exc, "code", default_code) or default_code).strip() or default_code
    extra = dict(getattr(exc, "extra", {}) or {})
    raise TrainingCenterError(status_code, str(exc), code, extra)


def _load_session_context(
    conn: sqlite3.Connection,
    session_id: str,
) -> tuple[sqlite3.Row, dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], list[str]]:
    row = _fetch_session_row(conn, session_id)
    session_summary = _session_row_to_summary(row)
    messages = _list_session_messages(conn, session_id)
    task_refs = _list_task_refs(conn, session_id)
    role_spec, missing_fields = _build_role_spec(messages)
    return row, session_summary, messages, task_refs, role_spec, missing_fields


def _update_session_role_spec(
    conn: sqlite3.Connection,
    *,
    session_id: str,
    session_summary: dict[str, Any] | None = None,
    messages: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[str], str]:
    if session_summary is None or messages is None:
        _row, session_summary, messages, _task_refs, _role_spec_unused, _missing_fields_unused = _load_session_context(
            conn,
            session_id,
        )
    role_spec, missing_fields = _build_role_spec(list(messages or []))
    session_title = _role_creation_title_from_spec(role_spec, (session_summary or {}).get("session_title") or "")
    status = _normalize_session_status((session_summary or {}).get("status"))
    current_stage_key = _normalize_stage_key(
        (session_summary or {}).get("current_stage_key") or "persona_collection",
    )
    current_stage_index = int((session_summary or {}).get("current_stage_index") or 2)
    if status == "draft":
        current_stage_key = "persona_collection"
        current_stage_index = 2
    conn.execute(
        """
        UPDATE role_creation_sessions
        SET session_title=?,role_spec_json=?,missing_fields_json=?,current_stage_key=?,current_stage_index=?,updated_at=?
        WHERE session_id=?
        """,
        (
            session_title,
            _json_dumps(role_spec),
            _json_dumps(missing_fields),
            current_stage_key,
            current_stage_index,
            _tc_now_text(),
            session_id,
        ),
    )
    if isinstance(session_summary, dict):
        session_summary["session_title"] = session_title
        session_summary["current_stage_key"] = current_stage_key
        session_summary["current_stage_index"] = current_stage_index
    return role_spec, missing_fields, session_title


def _role_creation_stage_update_text(stage_key: str) -> str:
    stage = dict(ROLE_CREATION_STAGE_BY_KEY.get(stage_key) or {})
    title = str(stage.get("title") or stage_key)
    return f"当前阶段切换为：{title}"


def _role_creation_default_artifact_name(stage_key: str, task_name: str) -> str:
    title = _normalize_text(task_name, max_len=60)
    normalized = re.sub(r'[<>:"/\\\\|?*\\x00-\\x1f]+', "-", title).strip().strip(".")
    if normalized:
        return f"{normalized}.html"
    mapping = {
        "persona_collection": "画像资料整理.html",
        "capability_generation": "能力样例草案.html",
        "review_and_alignment": "回看材料包.html",
    }
    return mapping.get(stage_key, "任务产物.html")


def _role_creation_current_task_ref_payload(
    detail: dict[str, Any],
    *,
    node_id: str,
) -> dict[str, Any]:
    task_refs = list(detail.get("task_refs") or [])
    stages = list(detail.get("stages") or [])
    ref_row = next(
        (item for item in task_refs if str(item.get("node_id") or "").strip() == str(node_id or "").strip()),
        {},
    )
    task_row = {}
    for stage in stages:
        for item in list(stage.get("active_tasks") or []) + list(stage.get("archived_tasks") or []):
            if str(item.get("node_id") or "").strip() == str(node_id or "").strip():
                task_row = dict(item)
                break
        if task_row:
            break
    payload = dict(task_row)
    payload.setdefault("ref_id", str(ref_row.get("ref_id") or "").strip())
    payload.setdefault("relation_state", str(ref_row.get("relation_state") or "active").strip().lower() or "active")
    payload.setdefault("close_reason", str(ref_row.get("close_reason") or "").strip())
    return payload


def _create_role_creation_task_internal(
    cfg: Any,
    *,
    session_summary: dict[str, Any],
    task_refs: list[dict[str, Any]],
    stage_key: str,
    node_name: str,
    node_goal: str,
    expected_artifact: str,
    operator: str,
    priority: str = "",
) -> dict[str, Any]:
    stage_key = _normalize_stage_key(stage_key)
    ticket_id = str(session_summary.get("assignment_ticket_id") or "").strip()
    if not ticket_id:
        raise TrainingCenterError(409, "当前角色还未进入创建流程", "role_creation_not_started")
    assigned_agent_id = str(session_summary.get("created_agent_id") or "").strip()
    assigned_agent_name = str(session_summary.get("created_agent_name") or assigned_agent_id or "").strip()
    if not assigned_agent_id:
        raise TrainingCenterError(409, "当前角色执行主体未初始化", "role_creation_agent_not_initialized")
    stage_index = int((ROLE_CREATION_STAGE_BY_KEY.get(stage_key) or {}).get("index") or 0)
    requested_priority = _normalize_text(priority, max_len=4).upper()
    if requested_priority not in {"P0", "P1", "P2", "P3"}:
        requested_priority = "P0" if stage_key == "persona_collection" else "P1"
    upstream_node_ids = _stage_anchor_task_ids(task_refs, stage_key=stage_key)
    node_payload = {
        "node_name": _normalize_text(node_name, max_len=200),
        "assigned_agent_id": assigned_agent_id,
        "node_goal": _normalize_text(node_goal, max_len=4000),
        "expected_artifact": _normalize_text(expected_artifact, max_len=240),
        "priority": requested_priority,
        "upstream_node_ids": upstream_node_ids,
        "operator": operator,
    }
    if not node_payload["node_name"]:
        raise TrainingCenterError(400, "任务名称不能为空", "role_creation_task_name_required")
    if not node_payload["node_goal"]:
        raise TrainingCenterError(400, "任务目标不能为空", "role_creation_task_goal_required")
    try:
        created = assignment_service.create_assignment_node(
            cfg,
            ticket_id,
            node_payload,
            include_test_data=True,
        )
    except Exception as exc:
        _raise_role_creation_assignment_error(exc, "role_creation_task_create_failed")
    node = dict(created.get("node") or {})
    now_text = _tc_now_text()
    conn = connect_db(cfg.root)
    try:
        conn.execute(
            """
            INSERT INTO role_creation_task_refs (
                ref_id,session_id,ticket_id,node_id,stage_key,stage_index,relation_state,close_reason,created_at,updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(session_id,node_id) DO UPDATE SET
                ticket_id=excluded.ticket_id,
                stage_key=excluded.stage_key,
                stage_index=excluded.stage_index,
                relation_state='active',
                close_reason='',
                updated_at=excluded.updated_at
            """,
            (
                _role_creation_task_ref_id(),
                str(session_summary.get("session_id") or "").strip(),
                ticket_id,
                str(node.get("node_id") or "").strip(),
                stage_key,
                stage_index,
                "active",
                "",
                now_text,
                now_text,
            ),
        )
        conn.execute(
            """
            UPDATE role_creation_sessions
            SET current_stage_key=?,current_stage_index=?,updated_at=?
            WHERE session_id=?
            """,
            (
                stage_key,
                stage_index,
                now_text,
                str(session_summary.get("session_id") or "").strip(),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return {
        "ticket_id": ticket_id,
        "stage_key": stage_key,
        "stage_index": stage_index,
        "task_id": str(node.get("node_id") or "").strip(),
        "node_id": str(node.get("node_id") or "").strip(),
        "task_name": str(node.get("node_name") or node_payload["node_name"]).strip(),
        "status": str(node.get("status") or "pending").strip().lower() or "pending",
        "status_text": str(node.get("status_text") or "待开始").strip() or "待开始",
        "assigned_agent_id": assigned_agent_id,
        "assigned_agent_name": assigned_agent_name,
    }


def _maybe_create_delegate_tasks(
    cfg: Any,
    *,
    session_summary: dict[str, Any],
    task_refs: list[dict[str, Any]],
    role_spec: dict[str, Any],
    message_text: str,
    operator: str,
) -> list[dict[str, Any]]:
    if _normalize_session_status(session_summary.get("status")) != "creating":
        return []
    delegate_requests = _delegate_requests_from_text(message_text)
    if not delegate_requests:
        return []
    role_name = _role_creation_title_from_spec(role_spec, session_summary.get("session_title") or "")
    created_tasks: list[dict[str, Any]] = []
    known_refs = list(task_refs)
    for clause in delegate_requests[:3]:
        stage_key = _infer_task_stage_key(clause, str(session_summary.get("current_stage_key") or "persona_collection"))
        task_name = _delegate_task_title(clause, role_name)
        expected_artifact = _role_creation_default_artifact_name(stage_key, task_name)
        task = _create_role_creation_task_internal(
            cfg,
            session_summary=session_summary,
            task_refs=known_refs,
            stage_key=stage_key,
            node_name=task_name,
            node_goal=clause,
            expected_artifact=expected_artifact,
            operator=operator,
        )
        created_tasks.append(task)
        known_refs.append(
            {
                "session_id": str(session_summary.get("session_id") or "").strip(),
                "ticket_id": str(task.get("ticket_id") or "").strip(),
                "node_id": str(task.get("node_id") or "").strip(),
                "stage_key": stage_key,
                "stage_index": int(task.get("stage_index") or 0),
                "relation_state": "active",
                "close_reason": "",
            }
        )
        session_summary["current_stage_key"] = stage_key
        session_summary["current_stage_index"] = int(task.get("stage_index") or 0)
    return created_tasks
