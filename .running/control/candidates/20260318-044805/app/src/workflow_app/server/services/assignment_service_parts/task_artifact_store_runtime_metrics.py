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
    snapshot = _assignment_snapshot_from_files(
        root,
        ticket_id,
        include_test_data=include_test_data,
        reconcile_running=True,
    )
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


def get_assignment_runtime_metrics(root: Path, *, include_test_data: bool = True) -> dict[str, int]:
    active_run_ids = {
        str(run_id or "").strip()
        for run_id in _active_assignment_run_ids()
        if str(run_id or "").strip()
    }
    now_dt = now_local()
    running_node_count = 0
    running_agents: set[str] = set()
    for ticket_id in _assignment_list_ticket_ids(root):
        try:
            task_record = _assignment_load_task_record(root, ticket_id)
        except AssignmentCenterError:
            continue
        if not _assignment_task_visible(task_record, include_test_data=include_test_data):
            continue
        node_lookup = {
            str(node.get("node_id") or "").strip(): dict(node)
            for node in _assignment_active_node_records(_assignment_load_node_records(root, ticket_id, include_deleted=True))
        }
        for run in _assignment_load_run_records(root, ticket_id=ticket_id):
            status = str(run.get("status") or "").strip().lower()
            if status not in {"starting", "running"}:
                continue
            if not _assignment_run_row_is_live(
                run,
                active_run_ids=active_run_ids,
                now_dt=now_dt,
                grace_seconds=DEFAULT_ASSIGNMENT_STALE_RUN_GRACE_SECONDS,
            ):
                continue
            node_id = str(run.get("node_id") or "").strip()
            node = node_lookup.get(node_id) or {}
            running_node_count += 1
            agent_id = str(node.get("assigned_agent_id") or "").strip()
            if agent_id:
                running_agents.add(agent_id)
    return {
        "running_task_count": max(0, running_node_count),
        "running_agent_count": max(0, len(running_agents)),
        "active_execution_count": max(0, running_node_count),
        "agent_call_count": max(0, running_node_count),
    }
