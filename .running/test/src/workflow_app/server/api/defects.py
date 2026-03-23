from __future__ import annotations

import re

from ..bootstrap import web_server_runtime as ws


def _defect_error_payload(exc: BaseException) -> tuple[int, dict]:
    if isinstance(exc, ws.DefectCenterError):
        payload = {"ok": False, "error": str(exc), "code": exc.code}
        payload.update(exc.extra)
        return exc.status_code, payload
    return 500, {"ok": False, "error": str(exc), "code": "defect_internal_error"}


def try_handle_get(handler, cfg, state, ctx: dict) -> bool:
    path = str(ctx.get("path") or "")
    query = ctx.get("query") or {}
    include_test_data = ws.resolve_include_test_data(query, cfg, state)
    policy_fields = ws.show_test_data_policy_fields(cfg, state)

    if path == "/api/defects":
        try:
            data = ws.list_defect_reports(
                cfg.root,
                include_test_data=include_test_data,
                status_filter=str((query.get("status") or [""])[0] or "").strip(),
                keyword=str((query.get("keyword") or [""])[0] or "").strip(),
                limit=int((query.get("limit") or ["200"])[0] or "200"),
            )
            handler.send_json(200, {"ok": True, "include_test_data": include_test_data, **policy_fields, **data})
        except Exception as exc:
            status, payload = _defect_error_payload(exc)
            handler.send_json(status, payload)
        return True

    mdetail = re.fullmatch(r"/api/defects/([0-9A-Za-z._:-]+)", path)
    if mdetail:
        try:
            data = ws.get_defect_detail(
                cfg.root,
                ws.safe_token(mdetail.group(1), "", 160),
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, "include_test_data": include_test_data, **policy_fields, **data})
        except Exception as exc:
            status, payload = _defect_error_payload(exc)
            handler.send_json(status, payload)
        return True

    mhistory = re.fullmatch(r"/api/defects/([0-9A-Za-z._:-]+)/history", path)
    if mhistory:
        try:
            data = ws.get_defect_history(
                cfg.root,
                ws.safe_token(mhistory.group(1), "", 160),
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, "include_test_data": include_test_data, **policy_fields, **data})
        except Exception as exc:
            status, payload = _defect_error_payload(exc)
            handler.send_json(status, payload)
        return True

    return False


def try_handle_post(handler, cfg, state, ctx: dict) -> bool:
    path = str(ctx.get("path") or "")
    body = ctx.get("body") or {}
    include_test_data = bool(ws.current_show_test_data(cfg, state))

    if path == "/api/defects":
        try:
            data = ws.create_defect_report(cfg, body)
            handler.send_json(200, {"ok": True, **data})
        except Exception as exc:
            status, payload = _defect_error_payload(exc)
            handler.send_json(status, payload)
        return True

    mtext = re.fullmatch(r"/api/defects/([0-9A-Za-z._:-]+)/supplements/text", path)
    if mtext:
        try:
            data = ws.append_defect_text(
                cfg,
                ws.safe_token(mtext.group(1), "", 160),
                body,
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except Exception as exc:
            status, payload = _defect_error_payload(exc)
            handler.send_json(status, payload)
        return True

    mimages = re.fullmatch(r"/api/defects/([0-9A-Za-z._:-]+)/supplements/images", path)
    if mimages:
        try:
            data = ws.append_defect_images(
                cfg,
                ws.safe_token(mimages.group(1), "", 160),
                body,
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except Exception as exc:
            status, payload = _defect_error_payload(exc)
            handler.send_json(status, payload)
        return True

    mdispute = re.fullmatch(r"/api/defects/([0-9A-Za-z._:-]+)/dispute", path)
    if mdispute:
        try:
            data = ws.mark_defect_dispute(
                cfg,
                ws.safe_token(mdispute.group(1), "", 160),
                body,
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except Exception as exc:
            status, payload = _defect_error_payload(exc)
            handler.send_json(status, payload)
        return True

    mprocess = re.fullmatch(r"/api/defects/([0-9A-Za-z._:-]+)/process-task", path)
    if mprocess:
        if not handler.ensure_root_ready():
            return True
        try:
            data = ws.create_defect_process_task(
                cfg,
                ws.safe_token(mprocess.group(1), "", 160),
                body,
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except Exception as exc:
            status, payload = _defect_error_payload(exc)
            handler.send_json(status, payload)
        return True

    mreview = re.fullmatch(r"/api/defects/([0-9A-Za-z._:-]+)/review-task", path)
    if mreview:
        if not handler.ensure_root_ready():
            return True
        try:
            data = ws.create_defect_review_task(
                cfg,
                ws.safe_token(mreview.group(1), "", 160),
                body,
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except Exception as exc:
            status, payload = _defect_error_payload(exc)
            handler.send_json(status, payload)
        return True

    mversion = re.fullmatch(r"/api/defects/([0-9A-Za-z._:-]+)/resolved-version", path)
    if mversion:
        try:
            data = ws.write_defect_resolved_version(
                cfg,
                ws.safe_token(mversion.group(1), "", 160),
                body,
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except Exception as exc:
            status, payload = _defect_error_payload(exc)
            handler.send_json(status, payload)
        return True

    mstatus = re.fullmatch(r"/api/defects/([0-9A-Za-z._:-]+)/status", path)
    if mstatus:
        try:
            data = ws.update_defect_status(
                cfg,
                ws.safe_token(mstatus.group(1), "", 160),
                body,
                include_test_data=include_test_data,
            )
            handler.send_json(200, {"ok": True, **data})
        except Exception as exc:
            status, payload = _defect_error_payload(exc)
            handler.send_json(status, payload)
        return True

    return False
