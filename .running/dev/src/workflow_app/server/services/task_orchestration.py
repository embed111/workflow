from __future__ import annotations

from .work_record_store import (
    append_task_run_event_record,
    create_task_run_record,
    get_task_run_record,
    get_training_task_record,
    list_task_run_event_records,
    list_task_run_records,
    load_task_trace_payload,
    mark_task_run_status,
    task_run_paths,
    update_task_run_record,
    update_task_run_result_files,
    write_task_run_summary,
)

def bind_runtime_symbols(symbols: dict[str, object]) -> None:
    globals().update(symbols)

def _decref_session_lock(state: RuntimeState, session_id: str, lock: threading.Lock) -> None:
    with state.session_lock_guard:
        entry = state.session_locks.get(session_id)
        if entry is None or entry.lock is not lock:
            return
        entry.ref_count = max(0, int(entry.ref_count or 0) - 1)
        if entry.ref_count <= 0 and not entry.lock.locked():
            state.session_locks.pop(session_id, None)


def session_lock_for(state: RuntimeState, session_id: str) -> SessionLockEntry:
    with state.session_lock_guard:
        entry = state.session_locks.get(session_id)
        if entry is None:
            entry = SessionLockEntry()
            state.session_locks[session_id] = entry
        entry.ref_count += 1
        return entry


def acquire_generation_slot(state: RuntimeState, session_id: str) -> GenerationLease:
    entry = session_lock_for(state, session_id)
    lock = entry.lock
    lock.acquire()
    if not state.generation_semaphore.acquire(blocking=False):
        lock.release()
        _decref_session_lock(state, session_id, lock)
        raise ConcurrencyLimitError(
            f"generation concurrency limit reached ({MAX_GENERATION_CONCURRENCY})"
        )
    return GenerationLease(session_id=session_id, lock=lock)


def release_generation_slot(state: RuntimeState, lease: GenerationLease | None) -> None:
    if lease is None:
        return
    lock = lease.lock
    state.generation_semaphore.release()
    lock.release()
    _decref_session_lock(state, lease.session_id, lock)


def new_task_id() -> str:
    ts = now_local()
    return f"task-{date_key(ts)}-{uuid.uuid4().hex[:8]}"


def redact_command(parts: list[str]) -> list[str]:
    out: list[str] = []
    for item in parts:
        text = str(item)
        lower = text.lower()
        if any(key in lower for key in ["api_key", "token", "secret", "password"]):
            out.append("***")
            continue
        if text.startswith("sk-"):
            out.append("***")
            continue
        out.append(text)
    return out


def build_agent_command(
    cfg: AppConfig,
    task_id_text: str,
    session: dict[str, str],
    message: str,
    focus: str,
    write_targets: list[str],
) -> tuple[list[str], list[str]]:
    runner = (cfg.root / "scripts" / "task_agent_runner.py").resolve()
    if not runner.exists():
        runner = (WORKFLOW_APP_ROOT / "task_agent_runner.py").resolve()
    trace_file = task_trace_file(cfg.root, task_id_text)
    cmd = [
        sys.executable,
        "-u",
        str(runner),
        "--root",
        str(cfg.root),
        "--session-id",
        session["session_id"],
        "--agent",
        session["agent_name"],
        "--agent-search-root",
        session["agent_search_root"],
        "--focus",
        focus,
        "--message",
        message,
        "--trace-file",
        str(trace_file),
    ]
    for target in write_targets:
        cmd.extend(["--write-target", target])
    return cmd, redact_command(cmd)


def create_task_run(
    root: Path,
    task_id_text: str,
    session_id: str,
    agent_name: str,
    agent_search_root: str,
    message: str,
    command: list[str],
    command_display: list[str],
) -> None:
    create_task_run_record(
        root,
        {
            "task_id": task_id_text,
            "session_id": session_id,
            "agent_name": agent_name,
            "agent_search_root": agent_search_root,
            "default_agents_root": agent_search_root,
            "target_path": agent_search_root,
            "status": "pending",
            "message": message,
            "command_json": json.dumps(command, ensure_ascii=False),
            "command_display": json.dumps(command_display, ensure_ascii=False),
            "created_at": iso_ts(now_local()),
        },
    )


def append_task_event(
    root: Path,
    task_id_text: str,
    event_type: str,
    payload: dict[str, Any],
) -> int:
    return append_task_run_event_record(
        root,
        task_id_text,
        {
            "timestamp": iso_ts(now_local()),
            "event_type": event_type,
            "payload": dict(payload or {}),
        },
    )


def get_task_run(root: Path, task_id_text: str) -> dict[str, Any] | None:
    out = get_task_run_record(root, task_id_text)
    if not out:
        return None
    try:
        out["command"] = json.loads(str(out.get("command_display") or "[]"))
    except Exception:
        out["command"] = []
    return out


def list_session_task_runs(root: Path, session_id: str, limit: int = 200) -> list[dict[str, Any]]:
    rows = list_task_run_records(root, session_id=session_id, limit=max(1, min(limit, 2000)))
    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        try:
            item["command"] = json.loads(str(item.get("command_display") or "[]"))
        except Exception:
            item["command"] = []
        task_id_value = str(item.get("task_id") or "")
        item["trace_available"] = bool(task_id_value and task_trace_file(root, task_id_value).exists())
        out.append(item)
    return out


def list_task_events(root: Path, task_id_text: str, since_id: int, limit: int = 400) -> list[dict[str, Any]]:
    return list_task_run_event_records(
        root,
        task_id_text,
        since_id=max(0, since_id),
        limit=max(1, min(limit, 1000)),
    )


def update_task_run_result(
    root: Path,
    task_id_text: str,
    *,
    status: str,
    start_at: str | None,
    end_at: str | None,
    duration_ms: int | None,
    stdout_text: str,
    stderr_text: str,
    summary: str,
    ref: str,
) -> None:
    update_task_run_result_files(
        root,
        task_id_text,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        trace_payload=load_task_trace(root, task_id_text),
    )
    update_task_run_record(
        root,
        task_id_text,
        {
            "status": status,
            "start_at": start_at or "",
            "end_at": end_at or "",
            "duration_ms": duration_ms,
            "summary": summary,
            "ref": ref,
            "updated_at": iso_ts(now_local()),
        },
    )


def mark_task_status(root: Path, task_id_text: str, status: str, *, started_at: str | None = None) -> None:
    mark_task_run_status(root, task_id_text, status, started_at=started_at)


def task_run_file(root: Path, task_id_text: str) -> Path:
    return task_run_paths(root, task_id_text)["summary"]


def task_trace_file(root: Path, task_id_text: str) -> Path:
    return task_run_paths(root, task_id_text)["trace"]


def load_task_trace(root: Path, task_id_text: str) -> dict[str, Any]:
    return load_task_trace_payload(root, task_id_text)


def write_task_run_file(
    root: Path,
    task_id_text: str,
    *,
    session_id: str,
    agent_name: str,
    agent_search_root: str,
    status: str,
    start_at: str,
    end_at: str,
    duration_ms: int,
    command_display: list[str],
    stdout_text: str,
    stderr_text: str,
    summary: str,
) -> str:
    summary_ref = write_task_run_summary(
        root,
        task_id_text,
        session_id=session_id,
        agent_name=agent_name,
        agent_search_root=agent_search_root,
        status=status,
        start_at=start_at,
        end_at=end_at,
        duration_ms=duration_ms,
        command_display=command_display,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        summary=summary,
    )
    return relative_to_root(root, Path(summary_ref))


def set_runtime_task(state: RuntimeState, runtime: TaskRuntime | None, task_id_text: str) -> None:
    with state.task_runtime_lock:
        if runtime is None:
            state.active_tasks.pop(task_id_text, None)
        else:
            state.active_tasks[task_id_text] = runtime


def get_runtime_task(state: RuntimeState, task_id_text: str) -> TaskRuntime | None:
    with state.task_runtime_lock:
        return state.active_tasks.get(task_id_text)


def active_runtime_task_count(state: RuntimeState) -> int:
    with state.task_runtime_lock:
        return len(state.active_tasks)


def has_session_runtime_task(state: RuntimeState, session_id: str) -> bool:
    with state.task_runtime_lock:
        return any(rt.session_id == session_id for rt in state.active_tasks.values())


def training_workflow_has_running_task(root: Path, state: RuntimeState, workflow_id: str) -> bool:
    workflow = get_training_workflow(root, workflow_id)
    if not workflow:
        return False
    session_id = str(workflow.get("session_id") or "")
    if session_id and has_session_runtime_task(state, session_id):
        return True
    analysis_id = str(workflow.get("analysis_id") or "")
    if not analysis_id:
        return False
    task_record = get_training_task_record(root, analysis_id)
    return str((task_record or {}).get("status") or "") == "running"


def append_admin_event(
    root: Path,
    *,
    session_id: str,
    action: str,
    status: str,
    reason_tags: list[str],
    ref: str,
) -> None:
    persist_event(
        root,
        {
            "event_id": event_id(),
            "timestamp": iso_ts(now_local()),
            "session_id": session_id,
            "actor": "workflow",
            "stage": "governance",
            "action": action,
            "status": status,
            "latency_ms": 0,
            "task_id": "",
            "reason_tags": reason_tags,
            "ref": ref,
        },
    )


def execute_task_worker(
    cfg: AppConfig,
    state: RuntimeState,
    task_id_text: str,
    session: dict[str, str],
    message: str,
    focus: str,
    command: list[str],
    command_display: list[str],
) -> None:
    runtime = TaskRuntime(
        task_id=task_id_text,
        session_id=session["session_id"],
        agent_name=session["agent_name"],
    )
    set_runtime_task(state, runtime, task_id_text)
    append_task_event(
        cfg.root,
        task_id_text,
        "queued",
        {
            "task_id": task_id_text,
            "session_id": session["session_id"],
            "agent_name": session["agent_name"],
        },
    )
    lock: threading.Lock | None = None
    start_ts = now_local()
    start_at = iso_ts(start_ts)
    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []
    status = "failed"
    summary = ""
    ref = ""
    try:
        mark_task_status(cfg.root, task_id_text, "queued")
        lock = session_lock_for(state, session["session_id"])
        lock.acquire()
        state.generation_semaphore.acquire()
        if runtime.stop_event.is_set():
            status = "interrupted"
            summary = "interrupted before command start"
            append_task_event(cfg.root, task_id_text, "interrupted", {"reason": summary})
            return

        mark_task_status(cfg.root, task_id_text, "running", started_at=start_at)
        append_task_event(
            cfg.root,
            task_id_text,
            "running",
            {"task_id": task_id_text, "command": command_display},
        )
        runtime.process = subprocess.Popen(
            command,
            cwd=str(cfg.root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        append_task_event(
            cfg.root,
            task_id_text,
            "process_started",
            {"pid": int(runtime.process.pid)},
        )

        def read_stream(name: str, pipe: Any, collector: list[str]) -> None:
            if pipe is None:
                return
            pending: list[str] = []
            while True:
                chunk = pipe.read(1)
                if chunk == "":
                    break
                collector.append(chunk)
                pending.append(chunk)
                if chunk == "\n" or len(pending) >= 64:
                    text = "".join(pending)
                    pending.clear()
                    append_task_event(
                        cfg.root,
                        task_id_text,
                        f"{name}_chunk",
                        {"chunk": text},
                    )
                if runtime.stop_event.is_set() and runtime.process and runtime.process.poll() is not None:
                    break
            if pending:
                append_task_event(
                    cfg.root,
                    task_id_text,
                    f"{name}_chunk",
                    {"chunk": "".join(pending)},
                )

        t_out = threading.Thread(
            target=read_stream,
            args=("stdout", runtime.process.stdout, stdout_chunks),
            daemon=True,
        )
        t_err = threading.Thread(
            target=read_stream,
            args=("stderr", runtime.process.stderr, stderr_chunks),
            daemon=True,
        )
        t_out.start()
        t_err.start()
        rc = runtime.process.wait()
        t_out.join(timeout=2)
        t_err.join(timeout=2)
        if runtime.stop_event.is_set():
            status = "interrupted"
            summary = "process interrupted by user"
        elif rc == 0:
            status = "success"
            summary = "command completed successfully"
        else:
            status = "failed"
            summary = f"command exit code={rc}"
    except Exception as exc:
        status = "failed"
        summary = f"{exc.__class__.__name__}: {exc}"
        stderr_chunks.append(summary + "\n")
        append_task_event(
            cfg.root,
            task_id_text,
            "error",
            {"error": summary},
        )
    finally:
        end_ts = now_local()
        end_at = iso_ts(end_ts)
        duration_ms = max(0, int((end_ts - start_ts).total_seconds() * 1000))
        stdout_text = "".join(stdout_chunks)
        stderr_text = "".join(stderr_chunks)
        if not summary:
            summary = "no summary"
        assistant_reply = stdout_text.rstrip("\n")
        if status == "success" and assistant_reply:
            try:
                add_message(cfg.root, session["session_id"], "assistant", assistant_reply)
            except Exception:
                pass
        ref = write_task_run_file(
            cfg.root,
            task_id_text,
            session_id=session["session_id"],
            agent_name=session["agent_name"],
            agent_search_root=session["agent_search_root"],
            status=status,
            start_at=start_at,
            end_at=end_at,
            duration_ms=duration_ms,
            command_display=command_display,
            stdout_text=stdout_text,
            stderr_text=stderr_text,
            summary=summary,
        )
        update_task_run_result(
            cfg.root,
            task_id_text,
            status=status,
            start_at=start_at,
            end_at=end_at,
            duration_ms=duration_ms,
            stdout_text=stdout_text,
            stderr_text=stderr_text,
            summary=summary,
            ref=ref,
        )
        append_task_event(
            cfg.root,
            task_id_text,
            "done",
            {
                "task_id": task_id_text,
                "status": status,
                "summary": summary,
                "duration_ms": duration_ms,
                "ref": ref,
            },
        )
        persist_event(
            cfg.root,
            {
                "event_id": event_id(),
                "timestamp": iso_ts(now_local()),
                "session_id": session["session_id"],
                "actor": "agent",
                "stage": "chat",
                "action": "send_message",
                "status": "success" if status == "success" else "failed",
                "latency_ms": duration_ms,
                "task_id": task_id_text,
                "reason_tags": (
                    session_policy_reason_tags(session)
                    if status == "success"
                    else [status, *session_policy_reason_tags(session)]
                ),
                "ref": ref,
            },
        )
        persist_event(
            cfg.root,
            {
                "event_id": event_id(),
                "timestamp": iso_ts(now_local()),
                "session_id": session["session_id"],
                "actor": "workflow",
                "stage": "chat",
                "action": "task_execute",
                "status": "success" if status == "success" else "failed",
                "latency_ms": duration_ms,
                "task_id": task_id_text,
                "reason_tags": (
                    session_policy_reason_tags(session)
                    if status == "success"
                    else [status, *session_policy_reason_tags(session)]
                ),
                "ref": ref,
            },
        )
        try:
            refresh_status(cfg)
            sync_analysis_tasks(cfg.root)
            sync_training_workflows(cfg.root)
        except Exception:
            pass
        if lock is not None:
            state.generation_semaphore.release()
            lock.release()
        set_runtime_task(state, None, task_id_text)


def request_task_interrupt(cfg: AppConfig, state: RuntimeState, task_id_text: str) -> tuple[bool, str]:
    runtime = get_runtime_task(state, task_id_text)
    if runtime is None:
        row = get_task_run(cfg.root, task_id_text)
        if not row:
            return False, "task not found"
        status = str(row.get("status") or "")
        if status in {"pending", "queued"}:
            mark_task_status(cfg.root, task_id_text, "interrupted")
            append_task_event(cfg.root, task_id_text, "interrupted", {"reason": "cancelled before start"})
            return True, "interrupted"
        return False, f"task not running (status={status})"
    runtime.stop_event.set()
    runtime.interrupted = True
    append_task_event(cfg.root, task_id_text, "interrupt_requested", {"task_id": task_id_text})
    proc = runtime.process
    if proc is not None and proc.poll() is None:
        try:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        except Exception:
            pass
    return True, "interrupt requested"


