def _persist_role_creation_dialogue_fields(
    conn: sqlite3.Connection,
    *,
    session_id: str,
    dialogue_agent_name: str,
    dialogue_agent_workspace_path: str,
    dialogue_provider: str,
    trace_ref: str,
    updated_at: str,
    stage_key: str = "",
    stage_index: int = 0,
) -> None:
    if stage_key:
        conn.execute(
            """
            UPDATE role_creation_sessions
            SET dialogue_agent_name=?,dialogue_agent_workspace_path=?,dialogue_provider=?,last_dialogue_trace_ref=?,
                current_stage_key=?,current_stage_index=?,updated_at=?
            WHERE session_id=?
            """,
            (
                dialogue_agent_name,
                dialogue_agent_workspace_path,
                dialogue_provider,
                trace_ref,
                stage_key,
                stage_index,
                updated_at,
                session_id,
            ),
        )
        return
    conn.execute(
        """
        UPDATE role_creation_sessions
        SET dialogue_agent_name=?,dialogue_agent_workspace_path=?,dialogue_provider=?,last_dialogue_trace_ref=?,updated_at=?
        WHERE session_id=?
        """,
        (
            dialogue_agent_name,
            dialogue_agent_workspace_path,
            dialogue_provider,
            trace_ref,
            updated_at,
            session_id,
        ),
    )


def _pick_role_creation_turn_stage_key(
    *,
    session_summary: dict[str, Any],
    analyst_turn: dict[str, Any],
    created_tasks: list[dict[str, Any]],
) -> str:
    if _normalize_session_status(session_summary.get("status")) != "creating":
        return ""
    candidate = str(analyst_turn.get("suggested_stage_key") or "").strip().lower()
    if candidate not in ROLE_CREATION_ANALYST_STAGE_KEYS:
        candidate = ""
    if not candidate and created_tasks:
        candidate = str(created_tasks[-1].get("stage_key") or "").strip().lower()
    if candidate in {"", "workspace_init", "complete_creation"}:
        return ""
    if candidate not in ROLE_CREATION_STAGE_BY_KEY:
        return ""
    if candidate == str(session_summary.get("current_stage_key") or "").strip().lower():
        return ""
    return candidate


def _append_role_creation_scheduler_message(
    root: Path,
    *,
    session_id: str,
    content: str,
    meta: dict[str, Any],
) -> None:
    conn = connect_db(root)
    try:
        conn.execute("BEGIN")
        _append_message(
            conn,
            session_id=session_id,
            role="system",
            content=content,
            attachments=[],
            message_type="system_task_update",
            meta=meta,
        )
        conn.commit()
    finally:
        conn.close()


def _resume_role_creation_scheduler(
    cfg: Any,
    *,
    session_id: str,
    ticket_id: str,
    operator: str,
) -> dict[str, Any]:
    try:
        result = assignment_service.resume_assignment_scheduler(
            cfg.root,
            ticket_id_text=ticket_id,
            operator=operator,
            include_test_data=True,
        )
    except Exception as exc:
        _append_role_creation_scheduler_message(
            cfg.root,
            session_id=session_id,
            content="任务图已生成，但自动调度启动失败。",
            meta={
                "assignment_ticket_id": ticket_id,
                "scheduler_state": "idle",
                "scheduler_error": str(exc),
            },
        )
        return {}
    dispatched = list(result.get("dispatch_result", {}).get("dispatched") or [])
    if dispatched:
        _append_role_creation_scheduler_message(
            cfg.root,
            session_id=session_id,
            content="已启动后台任务：" + "；".join(
                [
                    str(item.get("node_name") or item.get("task_name") or item.get("node_id") or "").strip()
                    for item in dispatched[:3]
                    if str(item.get("node_name") or item.get("task_name") or item.get("node_id") or "").strip()
                ]
            ),
            meta={
                "assignment_ticket_id": ticket_id,
                "scheduler_state": "running",
                "task_ids": [
                    str(item.get("node_id") or "").strip()
                    for item in dispatched
                    if str(item.get("node_id") or "").strip()
                ],
                "dispatch_result": result.get("dispatch_result") or {},
            },
        )
    return result


def _dispatch_role_creation_scheduler(
    cfg: Any,
    *,
    ticket_id: str,
    operator: str,
) -> dict[str, Any]:
    try:
        return assignment_service.dispatch_assignment_next(
            cfg.root,
            ticket_id_text=ticket_id,
            operator=operator,
            include_test_data=True,
        )
    except Exception:
        return {}


def _finalize_role_creation_message_processing_failure(
    cfg: Any,
    *,
    session_id: str,
    message_ids: list[str],
    batch_id: str,
    operator: str,
    error_text: str,
) -> None:
    session_key = safe_token(session_id, "", 160)
    if not session_key:
        return
    normalized_error = _normalize_text(error_text, max_len=2000) or "未知错误"
    now_text = _tc_now_text()
    conn = connect_db(cfg.root)
    try:
        conn.execute("BEGIN")
        try:
            _fetch_session_row(conn, session_key)
        except TrainingCenterError as exc:
            if str(getattr(exc, "code", "") or "").strip() == "role_creation_session_not_found":
                conn.rollback()
                return
            raise
        _update_role_creation_user_message_processing_state(
            conn,
            session_id=session_key,
            message_ids=message_ids,
            processing_state="failed",
            batch_id=batch_id,
            error_text=normalized_error,
            started_at=now_text,
        )
        _append_message(
            conn,
            session_id=session_key,
            role="assistant",
            content="这轮分析暂时失败了。你可以继续补充消息，我会把未处理内容重新合并后再分析一次。",
            attachments=[],
            message_type="chat",
            meta={
                "dialogue_error": normalized_error,
                "processing_batch_id": batch_id,
                "processing_failure": True,
            },
            created_at=now_text,
        )
        failure_messages = _list_session_messages(conn, session_key)
        _update_role_creation_message_queue_state(
            conn,
            session_id=session_key,
            queue_status="failed",
            queue_error=normalized_error,
            batch_id=batch_id,
            started_at=now_text,
            updated_at=now_text,
            messages=failure_messages,
        )
        conn.commit()
    finally:
        conn.close()
    append_training_center_audit(
        cfg.root,
        action="role_creation_message_batch_failed",
        operator=operator,
        target_id=session_key,
        detail={
            "session_id": session_key,
            "message_ids": list(message_ids or []),
            "processing_batch_id": batch_id,
            "error": normalized_error,
        },
    )


def _process_role_creation_message_batch(
    cfg: Any,
    *,
    session_id: str,
    operator: str,
) -> bool:
    time.sleep(ROLE_CREATION_MESSAGE_BATCH_DEBOUNCE_S)
    session_key = safe_token(session_id, "", 160)
    if not session_key:
        return False
    batch_started_at = _tc_now_text()
    batch_id = safe_token(f"rcmb-{uuid.uuid4().hex[:10]}", f"rcmb-{uuid.uuid4().hex[:10]}", 120)
    batch_messages: list[dict[str, Any]] = []
    current_detail: dict[str, Any] = {}
    session_summary: dict[str, Any] = {}
    role_spec: dict[str, Any] = {}
    missing_fields: list[str] = []
    session_title = ""
    task_refs: list[dict[str, Any]] = []
    created_tasks: list[dict[str, Any]] = []
    analyst_turn: dict[str, Any] = {}
    conn = connect_db(cfg.root)
    try:
        conn.execute("BEGIN")
        _row, session_summary, messages, task_refs, role_spec, missing_fields = _load_session_context(conn, session_key)
        if _normalize_session_status(session_summary.get("status")) == "completed":
            _update_role_creation_message_queue_state(
                conn,
                session_id=session_key,
                queue_status="idle",
                updated_at=batch_started_at,
                messages=messages,
            )
            conn.commit()
            return False
        batch_messages = _role_creation_pending_batch_messages(messages)
        if not batch_messages:
            _update_role_creation_message_queue_state(
                conn,
                session_id=session_key,
                queue_status="idle",
                updated_at=batch_started_at,
                messages=messages,
            )
            conn.commit()
            return False
        _update_role_creation_user_message_processing_state(
            conn,
            session_id=session_key,
            message_ids=[str(item.get("message_id") or "").strip() for item in batch_messages],
            processing_state="processing",
            batch_id=batch_id,
            started_at=batch_started_at,
        )
        processing_messages = _list_session_messages(conn, session_key)
        _update_role_creation_message_queue_state(
            conn,
            session_id=session_key,
            queue_status="running",
            queue_error="",
            batch_id=batch_id,
            started_at=batch_started_at,
            updated_at=batch_started_at,
            messages=processing_messages,
        )
        conn.commit()
    finally:
        conn.close()
    try:
        current_detail = get_role_creation_session_detail(cfg.root, session_key)
        session_summary = dict(current_detail.get("session") or {})
        role_spec = dict(current_detail.get("role_spec") or {})
        missing_fields = list((current_detail.get("profile") or {}).get("missing_fields") or [])
        session_title = str(session_summary.get("session_title") or "").strip()
        task_refs = list(current_detail.get("task_refs") or [])
        batch_text = _role_creation_batch_prompt_text(batch_messages)
        analyst_turn = run_role_creation_analyst_dialogue(
            cfg,
            detail=current_detail,
            latest_user_message=batch_text,
            operator=operator,
        )
        created_tasks = _create_role_creation_tasks_from_intents(
            cfg,
            session_summary=session_summary,
            task_refs=task_refs,
            task_intents=list(analyst_turn.get("delegate_tasks") or []),
            operator=operator,
        )
        if not created_tasks:
            created_tasks = _maybe_create_delegate_tasks(
                cfg,
                session_summary=session_summary,
                task_refs=task_refs,
                role_spec=role_spec,
                message_text=batch_text,
                operator=operator,
            )
        assistant_reply = str(analyst_turn.get("assistant_reply") or "").strip()
        if not assistant_reply:
            assistant_reply = _build_assistant_reply(
                session_summary={**session_summary, "session_title": session_title},
                role_spec=role_spec,
                missing_fields=missing_fields,
                created_tasks=created_tasks,
            )
        next_stage_key = _pick_role_creation_turn_stage_key(
            session_summary=session_summary,
            analyst_turn=analyst_turn,
            created_tasks=created_tasks,
        )
        next_stage_index = int((ROLE_CREATION_STAGE_BY_KEY.get(next_stage_key) or {}).get("index") or 0)
        dialogue_trace_ref = str(analyst_turn.get("trace_ref") or "").strip()
        assistant_message: dict[str, Any] = {}
        assistant_created_at = _tc_now_text()
        final_counts: dict[str, int] = {}
        conn = connect_db(cfg.root)
        try:
            conn.execute("BEGIN")
            _persist_role_creation_dialogue_fields(
                conn,
                session_id=session_key,
                dialogue_agent_name=str(analyst_turn.get("dialogue_agent_name") or "").strip(),
                dialogue_agent_workspace_path=str(analyst_turn.get("dialogue_agent_workspace_path") or "").strip(),
                dialogue_provider=str(analyst_turn.get("provider") or ROLE_CREATION_ANALYST_PROVIDER).strip(),
                trace_ref=dialogue_trace_ref,
                updated_at=assistant_created_at,
                stage_key=next_stage_key,
                stage_index=next_stage_index,
            )
            if next_stage_key:
                _append_message(
                    conn,
                    session_id=session_key,
                    role="system",
                    content=_role_creation_stage_update_text(next_stage_key),
                    attachments=[],
                    message_type="system_stage_update",
                    meta={
                        "stage_key": next_stage_key,
                        "source": "analyst_dialogue",
                        "trace_ref": dialogue_trace_ref,
                        "processing_batch_id": batch_id,
                    },
                    created_at=assistant_created_at,
                )
            if created_tasks:
                task_names = [
                    str(item.get("task_name") or "").strip()
                    for item in created_tasks
                    if str(item.get("task_name") or "").strip()
                ]
                _append_message(
                    conn,
                    session_id=session_key,
                    role="system",
                    content="已创建后台任务：" + "；".join(task_names[:3]),
                    attachments=[],
                    message_type="system_task_update",
                    meta={
                        "created_tasks": created_tasks,
                        "task_ids": [
                            str(item.get("task_id") or "").strip()
                            for item in created_tasks
                            if str(item.get("task_id") or "").strip()
                        ],
                        "processing_batch_id": batch_id,
                    },
                    created_at=assistant_created_at,
                )
            assistant_message = _append_message(
                conn,
                session_id=session_key,
                role="assistant",
                content=assistant_reply,
                attachments=[],
                message_type="chat",
                meta={
                    "dialogue_agent_name": str(analyst_turn.get("dialogue_agent_name") or "").strip(),
                    "dialogue_agent_workspace_path": str(analyst_turn.get("dialogue_agent_workspace_path") or "").strip(),
                    "dialogue_provider": str(analyst_turn.get("provider") or ROLE_CREATION_ANALYST_PROVIDER).strip(),
                    "trace_ref": dialogue_trace_ref,
                    "delegate_task_count": len(created_tasks),
                    "contract_has_json": bool(analyst_turn.get("contract_has_json")),
                    "dialogue_error": str(analyst_turn.get("error") or "").strip(),
                    "processing_batch_id": batch_id,
                    "handled_message_ids": [
                        str(item.get("message_id") or "").strip()
                        for item in batch_messages
                        if str(item.get("message_id") or "").strip()
                    ],
                },
                created_at=assistant_created_at,
            )
            _update_role_creation_user_message_processing_state(
                conn,
                session_id=session_key,
                message_ids=[str(item.get("message_id") or "").strip() for item in batch_messages],
                processing_state="processed",
                batch_id=batch_id,
                started_at=batch_started_at,
                processed_at=assistant_created_at,
                assistant_message_id=str(assistant_message.get("message_id") or "").strip(),
            )
            final_messages = _list_session_messages(conn, session_key)
            pending_counts = _role_creation_user_message_counts(final_messages)
            final_counts = _update_role_creation_message_queue_state(
                conn,
                session_id=session_key,
                queue_status="pending" if pending_counts["unhandled"] > 0 else "idle",
                queue_error="",
                updated_at=assistant_created_at,
                messages=final_messages,
            )
            conn.commit()
        finally:
            conn.close()
        if created_tasks and str(session_summary.get("assignment_ticket_id") or "").strip():
            _dispatch_role_creation_scheduler(
                cfg,
                ticket_id=str(session_summary.get("assignment_ticket_id") or "").strip(),
                operator=operator,
            )
        if str(session_summary.get("created_agent_workspace_path") or "").strip():
            _sync_workspace_profile(cfg.root, session_summary, role_spec)
        append_training_center_audit(
            cfg.root,
            action="role_creation_message_batch_processed",
            operator=operator,
            target_id=session_key,
            detail={
                "session_id": session_key,
                "processing_batch_id": batch_id,
                "message_ids": [
                    str(item.get("message_id") or "").strip()
                    for item in batch_messages
                    if str(item.get("message_id") or "").strip()
                ],
                "assistant_message_id": str(assistant_message.get("message_id") or "").strip(),
                "created_task_count": len(created_tasks),
                "dialogue_agent_name": str(analyst_turn.get("dialogue_agent_name") or "").strip(),
                "dialogue_agent_workspace_path": str(analyst_turn.get("dialogue_agent_workspace_path") or "").strip(),
                "dialogue_provider": str(analyst_turn.get("provider") or "").strip(),
                "dialogue_trace_ref": str(analyst_turn.get("trace_ref") or "").strip(),
                "dialogue_error": str(analyst_turn.get("error") or "").strip(),
                "unhandled_user_message_count": int(final_counts.get("unhandled") or 0),
            },
        )
        return int(final_counts.get("unhandled") or 0) > 0
    except TrainingCenterError as exc:
        if str(getattr(exc, "code", "") or "").strip() == "role_creation_session_not_found":
            return False
        _finalize_role_creation_message_processing_failure(
            cfg,
            session_id=session_key,
            message_ids=[str(item.get("message_id") or "").strip() for item in batch_messages],
            batch_id=batch_id,
            operator=operator,
            error_text=str(exc),
        )
        return False
    except Exception as exc:
        _finalize_role_creation_message_processing_failure(
            cfg,
            session_id=session_key,
            message_ids=[str(item.get("message_id") or "").strip() for item in batch_messages],
            batch_id=batch_id,
            operator=operator,
            error_text=str(exc),
        )
        return False


def _run_role_creation_message_worker(
    cfg: Any,
    *,
    session_id: str,
    operator: str,
) -> None:
    try:
        while True:
            has_more = _process_role_creation_message_batch(
                cfg,
                session_id=session_id,
                operator=operator,
            )
            if not has_more:
                break
    finally:
        with _ROLE_CREATION_MESSAGE_WORKER_LOCK:
            current = _ROLE_CREATION_MESSAGE_WORKERS.get(session_id)
            if current is threading.current_thread():
                _ROLE_CREATION_MESSAGE_WORKERS.pop(session_id, None)


def _ensure_role_creation_message_worker(
    cfg: Any,
    *,
    session_id: str,
    operator: str,
) -> bool:
    session_key = safe_token(session_id, "", 160)
    if not session_key:
        return False
    with _ROLE_CREATION_MESSAGE_WORKER_LOCK:
        current = _ROLE_CREATION_MESSAGE_WORKERS.get(session_key)
        if current and current.is_alive():
            return False
        worker = threading.Thread(
            target=_run_role_creation_message_worker,
            kwargs={"cfg": cfg, "session_id": session_key, "operator": operator},
            name=f"role-creation-message-{session_key}",
            daemon=True,
        )
        _ROLE_CREATION_MESSAGE_WORKERS[session_key] = worker
        worker.start()
        return True


def create_role_creation_session(cfg: Any, body: dict[str, Any]) -> dict[str, Any]:
    _ensure_role_creation_tables(cfg.root)
    session_id = _role_creation_session_id()
    now_text = _tc_now_text()
    requested_title = _normalize_text(
        body.get("session_title") or body.get("title") or "未命名角色草稿",
        max_len=80,
    ) or "未命名角色草稿"
    dialogue_agent = _resolve_role_creation_dialogue_agent(cfg)
    conn = connect_db(cfg.root)
    try:
        conn.execute(
            """
            INSERT INTO role_creation_sessions (
                session_id,session_title,status,current_stage_key,current_stage_index,role_spec_json,missing_fields_json,
                assignment_ticket_id,created_agent_id,created_agent_name,created_agent_workspace_path,workspace_init_status,
                workspace_init_ref,dialogue_agent_name,dialogue_agent_workspace_path,dialogue_provider,last_dialogue_trace_ref,
                last_message_preview,last_message_at,started_at,completed_at,created_at,updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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
                str(dialogue_agent.get("agent_name") or "").strip(),
                str(dialogue_agent.get("workspace_path") or "").strip(),
                str(dialogue_agent.get("provider") or ROLE_CREATION_ANALYST_PROVIDER).strip(),
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
        detail={
            "session_id": session_id,
            "session_title": requested_title,
            "dialogue_agent_name": str(dialogue_agent.get("agent_name") or "").strip(),
            "dialogue_agent_workspace_path": str(dialogue_agent.get("workspace_path") or "").strip(),
            "dialogue_provider": str(dialogue_agent.get("provider") or ROLE_CREATION_ANALYST_PROVIDER).strip(),
        },
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
    client_message_id = safe_token(body.get("client_message_id"), "", 120)
    user_message: dict[str, Any] = {}
    conn = connect_db(cfg.root)
    try:
        conn.execute("BEGIN")
        _row, session_summary, _messages, _task_refs, _role_spec_existing, _missing_existing = _load_session_context(conn, session_key)
        if _normalize_session_status(session_summary.get("status")) == "completed":
            raise TrainingCenterError(409, "当前角色创建已完成，不能继续追加消息", "role_creation_session_completed")
        user_message = _append_message(
            conn,
            session_id=session_key,
            role=role,
            content=content,
            attachments=attachments,
            message_type="chat",
            meta={
                "client_message_id": client_message_id,
                "processing_state": "pending" if role == "user" else "processed",
            },
        )
        messages = _list_session_messages(conn, session_key)
        _update_session_role_spec(
            conn,
            session_id=session_key,
            session_summary=session_summary,
            messages=messages,
        )
        if role == "user":
            _update_role_creation_message_queue_state(
                conn,
                session_id=session_key,
                queue_status="pending",
                queue_error="",
                updated_at=str(user_message.get("created_at") or "").strip() or _tc_now_text(),
                messages=messages,
            )
        conn.commit()
    finally:
        conn.close()
    worker_started = False
    if role == "user":
        worker_started = _ensure_role_creation_message_worker(
            cfg,
            session_id=session_key,
            operator=operator,
        )
    append_training_center_audit(
        cfg.root,
        action="role_creation_message_posted",
        operator=operator,
        target_id=session_key,
        detail={
            "message_role": role,
            "content_preview": _message_preview(content, attachments),
            "attachment_count": len(attachments),
            "user_message_id": str(user_message.get("message_id") or "").strip(),
            "client_message_id": client_message_id,
            "queued_for_processing": role == "user",
            "worker_started": worker_started,
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
    if _role_creation_session_has_unhandled_messages(session_summary):
        raise TrainingCenterError(
            409,
            "当前还有未处理的对话消息，请等待分析完成后再开始创建",
            "role_creation_messages_unhandled",
            {
                "message_processing_status": str(session_summary.get("message_processing_status") or "").strip(),
                "unhandled_user_message_count": int(session_summary.get("unhandled_user_message_count") or 0),
            },
        )
    if not _session_can_start(role_spec):
        raise TrainingCenterError(
            409,
            "当前草案信息不足，不能开始创建",
            "role_creation_spec_incomplete",
            {"missing_fields": missing_fields, "missing_labels": _missing_field_labels(missing_fields)},
        )
    dialogue_agent = _resolve_role_creation_dialogue_agent(cfg)
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
                created_agent_workspace_path=?,workspace_init_status=?,workspace_init_ref=?,dialogue_agent_name=?,
                dialogue_agent_workspace_path=?,dialogue_provider=?,started_at=?,updated_at=?
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
                str(dialogue_agent.get("agent_name") or "").strip(),
                str(dialogue_agent.get("workspace_path") or "").strip(),
                str(dialogue_agent.get("provider") or ROLE_CREATION_ANALYST_PROVIDER).strip(),
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
            "dialogue_agent_name": str(dialogue_agent.get("agent_name") or "").strip(),
            "dialogue_agent_workspace_path": str(dialogue_agent.get("workspace_path") or "").strip(),
        },
    )
    _resume_role_creation_scheduler(
        cfg,
        session_id=session_key,
        ticket_id=ticket_id,
        operator=operator,
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


def delete_role_creation_session(cfg: Any, session_id: str, body: dict[str, Any]) -> dict[str, Any]:
    _ensure_role_creation_tables(cfg.root)
    session_key = safe_token(str(session_id or ""), "", 160)
    if not session_key:
        raise TrainingCenterError(400, "session_id required", "role_creation_session_id_required")
    operator = str(body.get("operator") or "web-user")
    detail = get_role_creation_session_detail(cfg.root, session_key)
    session_summary = dict(detail.get("session") or {})
    session_status = _normalize_session_status(session_summary.get("status"))
    if session_status == "creating":
        raise TrainingCenterError(
            409,
            "当前角色正在创建中，暂不支持删除，请先完成当前创建流程",
            "role_creation_delete_creating_blocked",
            {
                "assignment_ticket_id": str(session_summary.get("assignment_ticket_id") or "").strip(),
                "created_agent_name": str(session_summary.get("created_agent_name") or "").strip(),
            },
        )
    if _role_creation_session_processing_active(session_summary):
        raise TrainingCenterError(
            409,
            "当前对话仍在分析中，暂不支持删除，请等待处理完成后再删除",
            "role_creation_delete_processing_blocked",
            {
                "message_processing_status": str(session_summary.get("message_processing_status") or "").strip(),
                "unhandled_user_message_count": int(session_summary.get("unhandled_user_message_count") or 0),
            },
        )
    deleted_payload = dict(session_summary)
    deleted_message_count = len(list(detail.get("messages") or []))
    deleted_task_ref_count = len(list(detail.get("task_refs") or []))
    conn = connect_db(cfg.root)
    try:
        conn.execute("BEGIN")
        conn.execute("DELETE FROM role_creation_messages WHERE session_id=?", (session_key,))
        conn.execute("DELETE FROM role_creation_task_refs WHERE session_id=?", (session_key,))
        conn.execute("DELETE FROM role_creation_sessions WHERE session_id=?", (session_key,))
        conn.commit()
    finally:
        conn.close()
    append_training_center_audit(
        cfg.root,
        action="role_creation_session_deleted",
        operator=operator,
        target_id=session_key,
        detail={
            "session_id": session_key,
            "session_title": str(session_summary.get("session_title") or "").strip(),
            "status": session_status,
            "assignment_ticket_id": str(session_summary.get("assignment_ticket_id") or "").strip(),
            "created_agent_id": str(session_summary.get("created_agent_id") or "").strip(),
            "deleted_message_count": deleted_message_count,
            "deleted_task_ref_count": deleted_task_ref_count,
        },
    )
    return {
        "deleted_session": deleted_payload,
        "deleted_message_count": deleted_message_count,
        "deleted_task_ref_count": deleted_task_ref_count,
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
    if _role_creation_session_has_unhandled_messages(session_summary):
        raise TrainingCenterError(
            409,
            "当前还有未处理的对话消息，请等待分析完成后再确认完成",
            "role_creation_messages_unhandled",
            {
                "message_processing_status": str(session_summary.get("message_processing_status") or "").strip(),
                "unhandled_user_message_count": int(session_summary.get("unhandled_user_message_count") or 0),
            },
        )
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
import threading
import time


_ROLE_CREATION_MESSAGE_WORKER_LOCK = threading.Lock()
_ROLE_CREATION_MESSAGE_WORKERS: dict[str, threading.Thread] = {}


def _role_creation_session_processing_active(session_summary: dict[str, Any]) -> bool:
    return _normalize_role_creation_queue_state(
        (session_summary or {}).get("message_processing_status"),
        default="idle",
    ) in {"pending", "running"}


def _role_creation_session_has_unhandled_messages(session_summary: dict[str, Any]) -> bool:
    try:
        return int((session_summary or {}).get("unhandled_user_message_count") or 0) > 0
    except Exception:
        return False


def _role_creation_pending_batch_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for message in list(messages or []):
        if str(message.get("role") or "").strip().lower() != "user":
            continue
        if _normalize_message_type(message.get("message_type")) != "chat":
            continue
        state = _normalize_role_creation_user_message_state(
            message.get("processing_state") or (message.get("meta") or {}).get("processing_state"),
            default="processed",
        )
        if state in {"pending", "failed"}:
            out.append(dict(message))
    return out


def _role_creation_batch_prompt_text(messages: list[dict[str, Any]]) -> str:
    rows = list(messages or [])
    if not rows:
        return ""
    if len(rows) == 1:
        only = dict(rows[0] or {})
        content = _normalize_text(only.get("content"), max_len=4000)
        if content:
            return content
        attachment_count = len(list(only.get("attachments") or []))
        if attachment_count > 0:
            return f"[本轮仅补充图片 {attachment_count} 张]"
        return ""
    parts: list[str] = []
    for index, message in enumerate(rows, start=1):
        item = dict(message or {})
        content = _normalize_text(item.get("content"), max_len=4000)
        attachment_count = len(list(item.get("attachments") or []))
        suffix = f" [附图 {attachment_count} 张]" if attachment_count > 0 else ""
        parts.append(f"{index}. {content or '[仅图片补充]'}{suffix}")
    return "本轮用户连续补充了多条消息，请合并处理：\n" + "\n".join(parts)


def _update_role_creation_user_message_processing_state(
    conn: sqlite3.Connection,
    *,
    session_id: str,
    message_ids: list[str],
    processing_state: str,
    batch_id: str = "",
    error_text: str = "",
    started_at: str = "",
    processed_at: str = "",
    assistant_message_id: str = "",
) -> None:
    ids = [safe_token(message_id, "", 160) for message_id in list(message_ids or [])]
    ids = [message_id for message_id in ids if message_id]
    if not ids:
        return
    state_value = _normalize_role_creation_user_message_state(processing_state, default="processed")
    for message_id in ids:
        row = conn.execute(
            """
            SELECT message_id,meta_json
            FROM role_creation_messages
            WHERE session_id=? AND message_id=?
            LIMIT 1
            """,
            (session_id, message_id),
        ).fetchone()
        if row is None:
            continue
        meta = _json_loads_dict(row["meta_json"])
        meta["processing_state"] = state_value
        if batch_id:
            meta["processing_batch_id"] = batch_id
        elif state_value != "processing":
            meta.pop("processing_batch_id", None)
        if state_value == "pending":
            meta["processing_error"] = ""
            meta.pop("processing_started_at", None)
            meta.pop("processed_at", None)
            meta.pop("assistant_message_id", None)
        elif state_value == "processing":
            meta["processing_error"] = ""
            if started_at:
                meta["processing_started_at"] = started_at
            meta.pop("processed_at", None)
            meta.pop("assistant_message_id", None)
        elif state_value == "processed":
            meta["processing_error"] = ""
            if started_at:
                meta["processing_started_at"] = started_at
            if processed_at:
                meta["processed_at"] = processed_at
            if assistant_message_id:
                meta["assistant_message_id"] = assistant_message_id
        else:
            meta["processing_error"] = _normalize_text(error_text, max_len=2000)
            if started_at:
                meta["processing_started_at"] = started_at
            meta.pop("processed_at", None)
            meta.pop("assistant_message_id", None)
        conn.execute(
            "UPDATE role_creation_messages SET meta_json=? WHERE message_id=?",
            (_json_dumps(meta), message_id),
        )
