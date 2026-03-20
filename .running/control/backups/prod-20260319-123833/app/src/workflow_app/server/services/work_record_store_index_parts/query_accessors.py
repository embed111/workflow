def _ordered_relpaths(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> list[str]:
    rows = conn.execute(sql, params).fetchall()
    out: list[str] = []
    for row in rows:
        relpath = str(row["relpath"] or "").strip()
        if relpath:
            out.append(relpath)
    return out


def _load_json_records_by_relpaths(root: Path, relpaths: list[str]) -> list[dict[str, Any]]:
    base = _store.artifact_root(root)
    rows: list[dict[str, Any]] = []
    for relpath in relpaths:
        payload = _store._load_json_dict(base / relpath)
        if payload:
            rows.append(payload)
    return rows


def list_session_records_from_index(root: Path, *, include_test_data: bool, limit: int) -> list[dict[str, Any]]:
    ensure_sqlite_index(root)
    conn = _connect(root)
    try:
        relpaths = _ordered_relpaths(
            conn,
            """
            SELECT session_relpath AS relpath
            FROM session_index
            WHERE (? = 1 OR is_test_data = 0)
            ORDER BY
                CASE WHEN status='active' THEN 0 ELSE 1 END,
                last_message_at DESC,
                session_id DESC
            LIMIT ?
            """,
            (1 if include_test_data else 0, max(1, min(int(limit), 2000))),
        )
    finally:
        conn.close()
    return _load_json_records_by_relpaths(root, relpaths)


def list_analysis_records_from_index(root: Path) -> list[dict[str, Any]]:
    ensure_sqlite_index(root)
    conn = _connect(root)
    try:
        relpaths = _ordered_relpaths(
            conn,
            "SELECT analysis_relpath AS relpath FROM analysis_index ORDER BY created_at ASC, analysis_id ASC",
            (),
        )
    finally:
        conn.close()
    return _load_json_records_by_relpaths(root, relpaths)


def list_workflow_records_from_index(root: Path) -> list[dict[str, Any]]:
    ensure_sqlite_index(root)
    conn = _connect(root)
    try:
        relpaths = _ordered_relpaths(
            conn,
            "SELECT workflow_relpath AS relpath FROM analysis_index WHERE workflow_relpath <> '' ORDER BY created_at ASC, analysis_id ASC",
            (),
        )
    finally:
        conn.close()
    return _load_json_records_by_relpaths(root, relpaths)


def list_task_run_records_from_index(root: Path, *, session_id: str, limit: int) -> list[dict[str, Any]]:
    ensure_sqlite_index(root)
    conn = _connect(root)
    try:
        relpaths = _ordered_relpaths(
            conn,
            """
            SELECT run_relpath AS relpath
            FROM task_run_index
            WHERE (? = '' OR session_id = ?)
            ORDER BY created_at DESC, task_id DESC
            LIMIT ?
            """,
            (str(session_id or ""), str(session_id or ""), max(1, min(int(limit), 2000))),
        )
    finally:
        conn.close()
    return _load_json_records_by_relpaths(root, relpaths)


def list_policy_patch_task_records_from_index(root: Path, *, limit: int) -> list[dict[str, Any]]:
    ensure_sqlite_index(root)
    conn = _connect(root)
    try:
        relpaths = _ordered_relpaths(
            conn,
            """
            SELECT source_relpath AS relpath
            FROM audit_index
            WHERE audit_type='policy_patch_task'
            ORDER BY created_at DESC, audit_key DESC
            LIMIT ?
            """,
            (max(1, min(int(limit), 2000)),),
        )
    finally:
        conn.close()
    return _load_json_records_by_relpaths(root, relpaths)


def find_analysis_id_for_run(root: Path, analysis_run_id: str) -> str:
    run_id = str(analysis_run_id or "").strip()
    if not run_id:
        return ""
    ensure_sqlite_index(root)
    conn = _connect(root)
    try:
        row = conn.execute(
            "SELECT analysis_id FROM analysis_run_index WHERE analysis_run_id=?",
            (run_id,),
        ).fetchone()
        return str(row["analysis_id"] or "") if row else ""
    finally:
        conn.close()


def find_analysis_id_by_workflow_id(root: Path, workflow_id: str) -> str:
    workflow_id_text = str(workflow_id or "").strip()
    if not workflow_id_text:
        return ""
    ensure_sqlite_index(root)
    conn = _connect(root)
    try:
        row = conn.execute(
            "SELECT analysis_id FROM analysis_index WHERE workflow_id=?",
            (workflow_id_text,),
        ).fetchone()
        return str(row["analysis_id"] or "") if row else ""
    finally:
        conn.close()


def latest_analysis_run_record_from_index(root: Path, analysis_id: str) -> dict[str, Any] | None:
    analysis_id_text = str(analysis_id or "").strip()
    if not analysis_id_text:
        return None
    ensure_sqlite_index(root)
    conn = _connect(root)
    try:
        row = conn.execute(
            """
            SELECT analysis_run_relpath
            FROM analysis_run_index
            WHERE analysis_id=?
            ORDER BY created_at DESC, analysis_run_id DESC
            LIMIT 1
            """,
            (analysis_id_text,),
        ).fetchone()
        relpath = str(row["analysis_run_relpath"] or "") if row else ""
    finally:
        conn.close()
    if not relpath:
        return None
    payload = _store._load_json_dict(_store.artifact_root(root) / relpath)
    return payload or None
