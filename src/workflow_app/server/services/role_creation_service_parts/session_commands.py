def create_role_creation_session(cfg: Any, body: dict[str, Any]) -> dict[str, Any]:
    _ensure_role_creation_tables(cfg.root)
    session_id = _role_creation_session_id()
    now_text = _tc_now_text()
    requested_title = _normalize_text(
        body.get("session_title") or body.get("title") or "未命名角色草稿",
        max_len=80,
    ) or "未命名角色草稿"
    conn = connect_db(cfg.root)
    try:
        conn.execute(
            """
            INSERT INTO role_creation_sessions (
                session_id,session_title,status,current_stage_key,current_stage_index,role_spec_json,missing_fields_json,
                assignment_ticket_id,created_agent_id,created_agent_name,created_agent_workspace_path,workspace_init_status,
                workspace_init_ref,last_message_preview,last_message_at,started_at,completed_at,created_at,updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                session_id,
                requested_title,
                "draft",
                "persona_collection",
                2,
                "{}",
                _json_dumps(list(ROLE_CREATION_ALL_FIELDS[:-1])),
                "",
                "",
                "",
                "",
                "pending",
                "",
                "",
                "",
                "",
                "",
                now_text,
                now_text,
            ),
        )
        _append_message(
            conn,
            session_id=session_id,
            role="assistant",
            content=(
                "先和我描述你想创建的角色。"
                "你可以直接发目标、能力、边界、适用场景，也可以把图片和文字一起发进同一条消息。"
            ),
            attachments=[],
            message_type="chat",
            created_at=now_text,
        )
        conn.commit()
    finally:
        conn.close()
    append_training_center_audit(
        cfg.root,
        action="role_creation_session_created",
        operator=str(body.get("operator") or "web-user"),
        target_id=session_id,
        detail={"session_id": session_id, "session_title": requested_title},
    )
    return get_role_creation_session_detail(cfg.root, session_id)


def post_role_creation_message(cfg: Any, session_id: str, body: dict[str, Any]) -> dict[str, Any]:
    _ensure_role_creation_tables(cfg.root)
    session_key = safe_token(str(session_id or ""), "", 160)
    if not session_key:
        raise TrainingCenterError(400, "session_id required", "role_creation_session_id_required")
    role = _normalize_text(body.get("role") or "user", max_len=20).lower() or "user"
    if role not in {"user", "assistant", "system"}:
        role = "user"
    content = _normalize_text(body.get("content"), max_len=4000)
    attachments = _normalize_message_attachments(body.get("attachments"))
    if not content and not attachments:
        raise TrainingCenterError(400, "消息内容不能为空", "role_creation_message_empty")
    operator = str(body.get("operator") or "web-user")
    created_tasks: list[dict[str, Any]] = []
    user_message: dict[str, Any] = {}
    session_summary: dict[str, Any] = {}
    role_spec: dict[str, Any] = {}
    missing_fields: list[str] = []
    session_title = ""
    task_refs: list[dict[str, Any]] = []
    conn = connect_db(cfg.root)
    try:
        conn.execute("BEGIN")
        _row, session_summary, _messages, task_refs, _role_spec_existing, _missing_existing = _load_session_context(conn, session_key)
        if _normalize_session_status(session_summary.get("status")) == "completed":
            raise TrainingCenterError(409, "当前角色创建已完成，不能继续追加消息", "role_creation_session_completed")
        user_message = _append_message(
            conn,
            session_id=session_key,
            role=role,
            content=content,
            attachments=attachments,
            message_type="chat",
        )
        messages = _list_session_messages(conn, session_key)
        role_spec, missing_fields, session_title = _update_session_role_spec(
            conn,
            session_id=session_key,
            session_summary=session_summary,
            messages=messages,
        )
        conn.commit()
    finally:
        conn.close()
    if role == "user":
        created_tasks = _maybe_create_delegate_tasks(
            cfg,
            session_summary=session_summary,
            task_refs=task_refs,
            role_spec=role_spec,
            message_text=content,
            operator=operator,
        )
        assistant_reply = _build_assistant_reply(
            session_summary={**session_summary, "session_title": session_title},
            role_spec=role_spec,
            missing_fields=missing_fields,
            created_tasks=created_tasks,
        )
        conn = connect_db(cfg.root)
        try:
            conn.execute("BEGIN")
            if created_tasks:
                task_names = [str(item.get("task_name") or "").strip() for item in created_tasks if str(item.get("task_name") or "").strip()]
                _append_message(
                    conn,
                    session_id=session_key,
                    role="system",
                    content="已创建后台任务：" + "；".join(task_names[:3]),
                    attachments=[],
                    message_type="system_task_update",
                    meta={
                        "created_tasks": created_tasks,
                        "task_ids": [str(item.get("task_id") or "").strip() for item in created_tasks if str(item.get("task_id") or "").strip()],
                    },
                )
            _append_message(
                conn,
                session_id=session_key,
                role="assistant",
                content=assistant_reply,
                attachments=[],
                message_type="chat",
            )
            conn.commit()
        finally:
            conn.close()
    append_training_center_audit(
        cfg.root,
        action="role_creation_message_posted",
        operator=operator,
        target_id=session_key,
        detail={
            "message_role": role,
            "content_preview": _message_preview(content, attachments),
            "attachment_count": len(attachments),
            "created_task_count": len(created_tasks),
            "user_message_id": str(user_message.get("message_id") or "").strip(),
        },
    )
    return get_role_creation_session_detail(cfg.root, session_key)


def start_role_creation_session(cfg: Any, session_id: str, body: dict[str, Any]) -> dict[str, Any]:
    _ensure_role_creation_tables(cfg.root)
    session_key = safe_token(str(session_id or ""), "", 160)
    if not session_key:
        raise TrainingCenterError(400, "session_id required", "role_creation_session_id_required")
    operator = str(body.get("operator") or "web-user")
    current_detail = get_role_creation_session_detail(cfg.root, session_key)
    session_summary = dict(current_detail.get("session") or {})
    role_spec = dict(current_detail.get("role_spec") or {})
    missing_fields = list((current_detail.get("profile") or {}).get("missing_fields") or [])
    status = _normalize_session_status(session_summary.get("status"))
    if status == "completed":
        raise TrainingCenterError(409, "当前角色创建已完成，不能再次启动", "role_creation_session_completed")
    if status == "creating" and str(session_summary.get("assignment_ticket_id") or "").strip():
        return current_detail
    if not _session_can_start(role_spec):
        raise TrainingCenterError(
            409,
            "当前草案信息不足，不能开始创建",
            "role_creation_spec_incomplete",
            {"missing_fields": missing_fields, "missing_labels": _missing_field_labels(missing_fields)},
        )
    workspace_result = _initialize_role_workspace(
        cfg,
        session_summary=session_summary,
        role_spec=role_spec,
    )
    _upsert_created_agent_registry_row(
        cfg.root,
        agent_id=str(workspace_result.get("created_agent_id") or "").strip(),
        agent_name=str(workspace_result.get("created_agent_name") or "").strip(),
        workspace_path=str(workspace_result.get("workspace_path") or "").strip(),
        role_spec=role_spec,
        runtime_status="creating",
    )
    starter_nodes = _starter_task_blueprint(
        role_spec,
        agent_id=str(workspace_result.get("created_agent_id") or "").strip(),
        agent_name=str(workspace_result.get("created_agent_name") or "").strip(),
    )
    graph_body = {
        "graph_name": f"{_role_creation_title_from_spec(role_spec, session_summary.get('session_title') or '')}创建工作流",
        "source_workflow": "training-role-creation",
        "summary": "训练中心创建角色工作流",
        "review_mode": "none",
        "external_request_id": session_key,
        "operator": operator,
        "nodes": [
            {
                "node_id": str(item.get("node_id") or "").strip(),
                "node_name": str(item.get("node_name") or "").strip(),
                "assigned_agent_id": str(item.get("assigned_agent_id") or "").strip(),
                "node_goal": str(item.get("node_goal") or "").strip(),
                "expected_artifact": str(item.get("expected_artifact") or "").strip(),
                "priority": str(item.get("priority") or "P1").strip(),
                "upstream_node_ids": list(item.get("upstream_node_ids") or []),
            }
            for item in starter_nodes
        ],
    }
    try:
        graph_result = assignment_service.create_assignment_graph(cfg, graph_body)
    except Exception as exc:
        _raise_role_creation_assignment_error(exc, "role_creation_start_graph_failed")
    ticket_id = str(graph_result.get("ticket_id") or "").strip()
    if not ticket_id:
        raise TrainingCenterError(500, "创建角色任务图失败", "role_creation_start_graph_missing_ticket")
    now_text = _tc_now_text()
    conn = connect_db(cfg.root)
    try:
        conn.execute("BEGIN")
        _fetch_session_row(conn, session_key)
        _insert_task_refs(
            conn,
            session_id=session_key,
            ticket_id=ticket_id,
            starter_nodes=starter_nodes,
            created_at=now_text,
        )
        conn.execute(
            """
            UPDATE role_creation_sessions
            SET status='creating',current_stage_key='persona_collection',current_stage_index=2,
                role_spec_json=?,missing_fields_json=?,assignment_ticket_id=?,created_agent_id=?,created_agent_name=?,
                created_agent_workspace_path=?,workspace_init_status=?,workspace_init_ref=?,started_at=?,updated_at=?
            WHERE session_id=?
            """,
            (
                _json_dumps(role_spec),
                _json_dumps(missing_fields),
                ticket_id,
                str(workspace_result.get("created_agent_id") or "").strip(),
                str(workspace_result.get("created_agent_name") or "").strip(),
                str(workspace_result.get("workspace_path") or "").strip(),
                str(workspace_result.get("workspace_init_status") or "completed").strip(),
                str(workspace_result.get("workspace_init_ref") or "").strip(),
                now_text,
                now_text,
                session_key,
            ),
        )
        _append_message(
            conn,
            session_id=session_key,
            role="system",
            content="阶段 1 已完成：真实角色工作区与记忆骨架初始化完成。",
            attachments=[],
            message_type="system_stage_update",
            meta={
                "stage_key": "workspace_init",
                "workspace_init_ref": str(workspace_result.get("workspace_init_ref") or "").strip(),
                "workspace_path": str(workspace_result.get("workspace_path") or "").strip(),
            },
            created_at=now_text,
        )
        _append_message(
            conn,
            session_id=session_key,
            role="system",
            content="已进入角色画像收集，并生成真实任务中心引用。",
            attachments=[],
            message_type="system_task_update",
            meta={
                "stage_key": "persona_collection",
                "assignment_ticket_id": ticket_id,
                "task_ids": [str(item.get("node_id") or "").strip() for item in starter_nodes],
            },
            created_at=now_text,
        )
        _append_message(
            conn,
            session_id=session_key,
            role="assistant",
            content="创建流程已启动。我会继续在当前会话里收口画像，并把后台任务推进情况同步回你。",
            attachments=[],
            message_type="chat",
            created_at=now_text,
        )
        conn.commit()
    finally:
        conn.close()
    append_training_center_audit(
        cfg.root,
        action="role_creation_started",
        operator=operator,
        target_id=session_key,
        detail={
            "session_id": session_key,
            "assignment_ticket_id": ticket_id,
            "created_agent_id": str(workspace_result.get("created_agent_id") or "").strip(),
            "workspace_init_ref": str(workspace_result.get("workspace_init_ref") or "").strip(),
        },
    )
    return get_role_creation_session_detail(cfg.root, session_key)


def update_role_creation_session_stage(cfg: Any, session_id: str, body: dict[str, Any]) -> dict[str, Any]:
    _ensure_role_creation_tables(cfg.root)
    session_key = safe_token(str(session_id or ""), "", 160)
    if not session_key:
        raise TrainingCenterError(400, "session_id required", "role_creation_session_id_required")
    stage_key = _normalize_stage_key(body.get("stage_key"))
    if stage_key == "complete_creation":
        raise TrainingCenterError(409, "完成角色创建请走独立完成接口", "role_creation_complete_stage_locked")
    operator = str(body.get("operator") or "web-user")
    reason = _normalize_text(body.get("reason") or body.get("note"), max_len=500)
    conn = connect_db(cfg.root)
    try:
        conn.execute("BEGIN")
        _row, session_summary, messages, _task_refs, _role_spec, _missing_fields = _load_session_context(conn, session_key)
        status = _normalize_session_status(session_summary.get("status"))
        if status == "completed":
            raise TrainingCenterError(409, "当前角色创建已完成，不能切换阶段", "role_creation_session_completed")
        if status != "creating":
            raise TrainingCenterError(409, "当前角色还未开始创建，不能切换阶段", "role_creation_not_started")
        stage_index = int((ROLE_CREATION_STAGE_BY_KEY.get(stage_key) or {}).get("index") or 0)
        conn.execute(
            """
            UPDATE role_creation_sessions
            SET current_stage_key=?,current_stage_index=?,updated_at=?
            WHERE session_id=?
            """,
            (stage_key, stage_index, _tc_now_text(), session_key),
        )
        _append_message(
            conn,
            session_id=session_key,
            role="system",
            content=_role_creation_stage_update_text(stage_key),
            attachments=[],
            message_type="system_stage_update",
            meta={"stage_key": stage_key, "reason": reason},
        )
        role_spec, _missing_fields, _title = _update_session_role_spec(
            conn,
            session_id=session_key,
            session_summary={**session_summary, "current_stage_key": stage_key, "current_stage_index": stage_index},
            messages=messages,
        )
        if str(session_summary.get("created_agent_workspace_path") or "").strip():
            _sync_workspace_profile(cfg.root, session_summary, role_spec)
        conn.commit()
    finally:
        conn.close()
    append_training_center_audit(
        cfg.root,
        action="role_creation_stage_updated",
        operator=operator,
        target_id=session_key,
        detail={"stage_key": stage_key, "reason": reason},
    )
    return get_role_creation_session_detail(cfg.root, session_key)


def create_role_creation_task(cfg: Any, session_id: str, body: dict[str, Any]) -> dict[str, Any]:
    _ensure_role_creation_tables(cfg.root)
    session_key = safe_token(str(session_id or ""), "", 160)
    if not session_key:
        raise TrainingCenterError(400, "session_id required", "role_creation_session_id_required")
    detail = get_role_creation_session_detail(cfg.root, session_key)
    session_summary = dict(detail.get("session") or {})
    task_refs = list(detail.get("task_refs") or [])
    if _normalize_session_status(session_summary.get("status")) != "creating":
        raise TrainingCenterError(409, "当前角色还未进入创建流程", "role_creation_not_started")
    stage_key = _normalize_stage_key(
        body.get("stage_key")
        or _infer_task_stage_key(
            str(body.get("node_goal") or body.get("goal") or body.get("content") or ""),
            str(session_summary.get("current_stage_key") or "persona_collection"),
        )
    )
    node_name = _normalize_text(
        body.get("node_name") or body.get("task_name") or body.get("title"),
        max_len=200,
    )
    node_goal = _normalize_text(
        body.get("node_goal") or body.get("goal") or body.get("content"),
        max_len=4000,
    )
    if not node_name and node_goal:
        node_name = _delegate_task_title(node_goal, str(session_summary.get("session_title") or ""))
    expected_artifact = _normalize_text(
        body.get("expected_artifact"),
        max_len=240,
    ) or _role_creation_default_artifact_name(stage_key, node_name)
    operator = str(body.get("operator") or "web-user")
    created_task = _create_role_creation_task_internal(
        cfg,
        session_summary=session_summary,
        task_refs=task_refs,
        stage_key=stage_key,
        node_name=node_name,
        node_goal=node_goal,
        expected_artifact=expected_artifact,
        operator=operator,
        priority=str(body.get("priority") or "").strip(),
    )
    conn = connect_db(cfg.root)
    try:
        conn.execute("BEGIN")
        _append_message(
            conn,
            session_id=session_key,
            role="system",
            content="已新建后台任务：" + str(created_task.get("task_name") or "").strip(),
            attachments=[],
            message_type="system_task_update",
            meta={"created_task": created_task, "stage_key": stage_key},
        )
        conn.commit()
    finally:
        conn.close()
    append_training_center_audit(
        cfg.root,
        action="role_creation_task_created",
        operator=operator,
        target_id=session_key,
        detail=created_task,
    )
    updated = get_role_creation_session_detail(cfg.root, session_key)
    created_task_payload = dict(created_task)
    for key, value in _role_creation_current_task_ref_payload(
        updated,
        node_id=str(created_task.get("node_id") or "").strip(),
    ).items():
        if key not in created_task_payload or value not in ("", [], {}, None):
            created_task_payload[key] = value
    return {
        **updated,
        "created_task": created_task_payload,
    }


def archive_role_creation_task(cfg: Any, session_id: str, node_id: str, body: dict[str, Any]) -> dict[str, Any]:
    _ensure_role_creation_tables(cfg.root)
    session_key = safe_token(str(session_id or ""), "", 160)
    node_key = safe_token(str(node_id or ""), "", 160)
    if not session_key:
        raise TrainingCenterError(400, "session_id required", "role_creation_session_id_required")
    if not node_key:
        raise TrainingCenterError(400, "node_id required", "role_creation_node_id_required")
    operator = str(body.get("operator") or "web-user")
    close_reason = _normalize_text(body.get("close_reason") or body.get("reason"), max_len=500)
    if not close_reason:
        raise TrainingCenterError(400, "归档原因不能为空", "role_creation_archive_reason_required")
    detail = get_role_creation_session_detail(cfg.root, session_key)
    ref_row = next(
        (item for item in list(detail.get("task_refs") or []) if str(item.get("node_id") or "").strip() == node_key),
        {},
    )
    if not ref_row:
        raise TrainingCenterError(404, "任务引用不存在", "role_creation_task_ref_not_found")
    task_payload = _role_creation_current_task_ref_payload(detail, node_id=node_key)
    if str(task_payload.get("status") or "").strip().lower() == "running":
        raise TrainingCenterError(409, "运行中的任务不能直接归档", "role_creation_archive_running_task_blocked")
    now_text = _tc_now_text()
    conn = connect_db(cfg.root)
    try:
        conn.execute("BEGIN")
        conn.execute(
            """
            UPDATE role_creation_task_refs
            SET relation_state='archived',close_reason=?,updated_at=?
            WHERE session_id=? AND node_id=?
            """,
            (close_reason, now_text, session_key, node_key),
        )
        _append_message(
            conn,
            session_id=session_key,
            role="system",
            content="已把后台任务收口到废案收纳：" + str(task_payload.get("task_name") or node_key).strip(),
            attachments=[],
            message_type="system_task_update",
            meta={"node_id": node_key, "close_reason": close_reason, "relation_state": "archived"},
            created_at=now_text,
        )
        conn.commit()
    finally:
        conn.close()
    append_training_center_audit(
        cfg.root,
        action="role_creation_task_archived",
        operator=operator,
        target_id=session_key,
        detail={"node_id": node_key, "close_reason": close_reason},
    )
    updated = get_role_creation_session_detail(cfg.root, session_key)
    return {
        **updated,
        "archived_task": _role_creation_current_task_ref_payload(updated, node_id=node_key),
    }


def complete_role_creation_session(cfg: Any, session_id: str, body: dict[str, Any]) -> dict[str, Any]:
    _ensure_role_creation_tables(cfg.root)
    session_key = safe_token(str(session_id or ""), "", 160)
    if not session_key:
        raise TrainingCenterError(400, "session_id required", "role_creation_session_id_required")
    confirmed = _parse_bool_flag(
        body.get("confirmed")
        if "confirmed" in body
        else body.get("acceptance_confirmed"),
        default=False,
    )
    if not confirmed:
        raise TrainingCenterError(409, "必须在用户明确确认后才能完成角色创建", "role_creation_confirmation_required")
    operator = str(body.get("operator") or "web-user")
    acceptance_note = _normalize_text(body.get("acceptance_note") or body.get("note"), max_len=500)
    detail = get_role_creation_session_detail(cfg.root, session_key)
    session_summary = dict(detail.get("session") or {})
    role_spec = dict(detail.get("role_spec") or {})
    if _normalize_session_status(session_summary.get("status")) != "creating":
        raise TrainingCenterError(409, "当前角色不在创建中，不能完成创建", "role_creation_not_started")
    unresolved_tasks = []
    for stage in list(detail.get("stages") or []):
        for task in list(stage.get("active_tasks") or []):
            if str(task.get("status") or "").strip().lower() != "succeeded":
                unresolved_tasks.append(
                    {
                        "node_id": str(task.get("node_id") or "").strip(),
                        "task_name": str(task.get("task_name") or "").strip(),
                        "status": str(task.get("status") or "").strip().lower(),
                        "status_text": str(task.get("status_text") or "").strip(),
                    }
                )
    if unresolved_tasks:
        raise TrainingCenterError(
            409,
            "仍有未完成的后台任务，不能完成角色创建",
            "role_creation_tasks_incomplete",
            {"unresolved_tasks": unresolved_tasks[:12]},
        )
    now_text = _tc_now_text()
    conn = connect_db(cfg.root)
    try:
        conn.execute("BEGIN")
        conn.execute(
            """
            UPDATE role_creation_sessions
            SET status='completed',current_stage_key='complete_creation',current_stage_index=6,
                role_spec_json=?,missing_fields_json=?,completed_at=?,updated_at=?
            WHERE session_id=?
            """,
            (
                _json_dumps(role_spec),
                _json_dumps([]),
                now_text,
                now_text,
                session_key,
            ),
        )
        _append_message(
            conn,
            session_id=session_key,
            role="system",
            content="用户已确认通过验收，角色创建完成。",
            attachments=[],
            message_type="system_result",
            meta={"stage_key": "complete_creation", "acceptance_note": acceptance_note},
            created_at=now_text,
        )
        _append_message(
            conn,
            session_id=session_key,
            role="assistant",
            content="角色创建已完成，后续可以直接进入训练闭环和版本治理。",
            attachments=[],
            message_type="chat",
            created_at=now_text,
        )
        conn.commit()
    finally:
        conn.close()
    _update_agent_runtime_status(
        cfg.root,
        agent_id=str(session_summary.get("created_agent_id") or "").strip(),
        runtime_status="idle",
    )
    _sync_workspace_profile(cfg.root, session_summary, role_spec)
    append_training_center_audit(
        cfg.root,
        action="role_creation_completed",
        operator=operator,
        target_id=session_key,
        detail={
            "created_agent_id": str(session_summary.get("created_agent_id") or "").strip(),
            "acceptance_note": acceptance_note,
        },
    )
    return get_role_creation_session_detail(cfg.root, session_key)
