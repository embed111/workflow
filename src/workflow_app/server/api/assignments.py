from __future__ import annotations

import re

from ..bootstrap import web_server_runtime as ws


def _parse_int_query(query: dict, key: str, default: int) -> int:
    try:
        return int((query.get(key) or [str(default)])[0])
    except Exception:
        return int(default)


def try_handle_get(handler, cfg, state, ctx: dict) -> bool:
    path = str(ctx.get("path") or "")
    query = ctx.get("query") or {}
    include_test_data = ws.resolve_include_test_data(query, cfg, state)

    if path.startswith("/api/assignments") and not handler.ensure_root_ready():
        return True

    if path == "/api/assignments/settings/concurrency":
        data = ws.get_assignment_concurrency_settings(cfg.root)
        handler.send_json(200, {"ok": True, **data})
        return True

    martifact_preview = re.fullmatch(
        r"/api/assignments/([0-9A-Za-z._:-]+)/nodes/([0-9A-Za-z._:-]+)/artifact-preview",
        path,
    )
    if martifact_preview:
        try:
            data = ws.read_assignment_artifact_preview(
                cfg.root,
                ticket_id_text=ws.safe_token(martifact_preview.group(1), "", 160),
                node_id_text=ws.safe_token(martifact_preview.group(2), "", 160),
                include_test_data=include_test_data,
            )
            handler.send_text(200, str(data.get("content") or ""), str(data.get("content_type") or "text/plain; charset=utf-8"))
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    if path == "/api/assignments":
        data = ws.list_assignments(cfg.root, include_test_data=include_test_data)
        handler.send_json(200, {"ok": True, **data})
        return True

    mgraph = re.fullmatch(r"/api/assignments/([0-9A-Za-z._:-]+)/graph", path)
    if mgraph:
        try:
            data = ws.get_assignment_graph(
                cfg.root,
                ws.safe_token(mgraph.group(1), "", 160),
                history_loaded=_parse_int_query(query, "history_loaded", 0),
                history_batch_size=_parse_int_query(query, "history_batch_size", 12),
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    mdetail = re.fullmatch(r"/api/assignments/([0-9A-Za-z._:-]+)/status-detail", path)
    if mdetail:
        try:
            data = ws.get_assignment_status_detail(
                cfg.root,
                ws.safe_token(mdetail.group(1), "", 160),
                node_id_text=str((query.get("node_id") or [""])[0] or "").strip(),
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    mscheduler = re.fullmatch(r"/api/assignments/([0-9A-Za-z._:-]+)/scheduler-state", path)
    if mscheduler:
        try:
            data = ws.get_assignment_scheduler_state(
                cfg.root,
                ws.safe_token(mscheduler.group(1), "", 160),
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    moverview = re.fullmatch(r"/api/assignments/([0-9A-Za-z._:-]+)", path)
    if moverview:
        try:
            data = ws.get_assignment_overview(
                cfg.root,
                ws.safe_token(moverview.group(1), "", 160),
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    return False


def try_handle_post(handler, cfg, state, ctx: dict) -> bool:
    path = str(ctx.get("path") or "")
    body = ctx.get("body") or {}
    current_include_test_data = ws.current_show_test_data(cfg, state)

    if path.startswith("/api/assignments") and not handler.ensure_root_ready():
        return True

    if path == "/api/assignments/settings/concurrency":
        try:
            data = ws.set_assignment_concurrency_settings(
                cfg.root,
                global_concurrency_limit=body.get("global_concurrency_limit"),
                operator=str(body.get("operator") or "web-user"),
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    if path == "/api/assignments":
        try:
            next_body = dict(body)
            if not current_include_test_data:
                next_body["is_test_data"] = False
            data = ws.create_assignment_graph(cfg, next_body)
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    if path == "/api/assignments/test-data/bootstrap":
        try:
            if not current_include_test_data:
                raise ws.AssignmentCenterError(
                    409,
                    "assignment test data hidden by global switch",
                    "assignment_test_data_hidden",
                )
            data = ws.bootstrap_assignment_test_graph(
                cfg,
                operator=str(body.get("operator") or "web-user"),
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    mnode = re.fullmatch(r"/api/assignments/([0-9A-Za-z._:-]+)/nodes", path)
    if mnode:
        try:
            data = ws.create_assignment_node(
                cfg,
                ws.safe_token(mnode.group(1), "", 160),
                body,
                include_test_data=current_include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    mdispatch = re.fullmatch(r"/api/assignments/([0-9A-Za-z._:-]+)/dispatch-next", path)
    if mdispatch:
        try:
            data = ws.dispatch_assignment_next(
                cfg.root,
                ticket_id_text=ws.safe_token(mdispatch.group(1), "", 160),
                operator=str(body.get("operator") or "web-user"),
                include_test_data=current_include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    mpause = re.fullmatch(r"/api/assignments/([0-9A-Za-z._:-]+)/pause", path)
    if mpause:
        try:
            data = ws.pause_assignment_scheduler(
                cfg.root,
                ticket_id_text=ws.safe_token(mpause.group(1), "", 160),
                operator=str(body.get("operator") or "web-user"),
                pause_note=body.get("pause_note") or body.get("note") or "",
                include_test_data=current_include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    mresume = re.fullmatch(r"/api/assignments/([0-9A-Za-z._:-]+)/resume", path)
    if mresume:
        try:
            data = ws.resume_assignment_scheduler(
                cfg.root,
                ticket_id_text=ws.safe_token(mresume.group(1), "", 160),
                operator=str(body.get("operator") or "web-user"),
                pause_note=body.get("pause_note") or body.get("note") or "",
                include_test_data=current_include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    mclear = re.fullmatch(r"/api/assignments/([0-9A-Za-z._:-]+)/clear", path)
    if mclear:
        try:
            data = ws.clear_assignment_graph(
                cfg.root,
                ticket_id_text=ws.safe_token(mclear.group(1), "", 160),
                operator=str(body.get("operator") or "web-user"),
                reason=body.get("reason") or "",
                include_test_data=current_include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    msuccess = re.fullmatch(
        r"/api/assignments/([0-9A-Za-z._:-]+)/nodes/([0-9A-Za-z._:-]+)/mark-success",
        path,
    )
    if msuccess:
        try:
            data = ws.mark_assignment_node_success(
                cfg.root,
                ticket_id_text=ws.safe_token(msuccess.group(1), "", 160),
                node_id_text=ws.safe_token(msuccess.group(2), "", 160),
                success_reason=body.get("success_reason"),
                result_ref=body.get("result_ref") or "",
                operator=str(body.get("operator") or "web-user"),
                include_test_data=current_include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    mdeliver = re.fullmatch(
        r"/api/assignments/([0-9A-Za-z._:-]+)/nodes/([0-9A-Za-z._:-]+)/deliver-artifact",
        path,
    )
    if mdeliver:
        try:
            data = ws.deliver_assignment_artifact(
                cfg.root,
                ticket_id_text=ws.safe_token(mdeliver.group(1), "", 160),
                node_id_text=ws.safe_token(mdeliver.group(2), "", 160),
                operator=str(body.get("operator") or "web-user"),
                artifact_label=body.get("artifact_label") or body.get("artifactLabel") or "",
                delivery_note=body.get("delivery_note") or body.get("deliveryNote") or "",
                include_test_data=current_include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    mfailed = re.fullmatch(
        r"/api/assignments/([0-9A-Za-z._:-]+)/nodes/([0-9A-Za-z._:-]+)/mark-failed",
        path,
    )
    if mfailed:
        try:
            data = ws.mark_assignment_node_failed(
                cfg.root,
                ticket_id_text=ws.safe_token(mfailed.group(1), "", 160),
                node_id_text=ws.safe_token(mfailed.group(2), "", 160),
                failure_reason=body.get("failure_reason"),
                operator=str(body.get("operator") or "web-user"),
                include_test_data=current_include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    mrerun = re.fullmatch(
        r"/api/assignments/([0-9A-Za-z._:-]+)/nodes/([0-9A-Za-z._:-]+)/rerun",
        path,
    )
    if mrerun:
        try:
            data = ws.rerun_assignment_node(
                cfg.root,
                ticket_id_text=ws.safe_token(mrerun.group(1), "", 160),
                node_id_text=ws.safe_token(mrerun.group(2), "", 160),
                operator=str(body.get("operator") or "web-user"),
                reason=body.get("reason") or "",
                include_test_data=current_include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    moverride = re.fullmatch(
        r"/api/assignments/([0-9A-Za-z._:-]+)/nodes/([0-9A-Za-z._:-]+)/override-status",
        path,
    )
    if moverride:
        try:
            data = ws.override_assignment_node_status(
                cfg.root,
                ticket_id_text=ws.safe_token(moverride.group(1), "", 160),
                node_id_text=ws.safe_token(moverride.group(2), "", 160),
                target_status=body.get("target_status") or body.get("status") or "",
                operator=str(body.get("operator") or "web-user"),
                reason=body.get("reason") or "",
                include_test_data=current_include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    return False


def try_handle_delete(handler, cfg, state, ctx: dict) -> bool:
    path = str(ctx.get("path") or "")
    body = ctx.get("body") or {}
    current_include_test_data = ws.current_show_test_data(cfg, state)

    if path.startswith("/api/assignments") and not handler.ensure_root_ready():
        return True

    mdelete_node = re.fullmatch(
        r"/api/assignments/([0-9A-Za-z._:-]+)/nodes/([0-9A-Za-z._:-]+)",
        path,
    )
    if mdelete_node:
        try:
            data = ws.delete_assignment_node(
                cfg.root,
                ticket_id_text=ws.safe_token(mdelete_node.group(1), "", 160),
                node_id_text=ws.safe_token(mdelete_node.group(2), "", 160),
                operator=str(body.get("operator") or "web-user"),
                reason=body.get("reason") or "",
                include_test_data=current_include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except ws.AssignmentCenterError as exc:
            payload = {"ok": False, "error": str(exc), "code": exc.code}
            payload.update(exc.extra)
            handler.send_json(exc.status_code, payload)
        return True

    return False
