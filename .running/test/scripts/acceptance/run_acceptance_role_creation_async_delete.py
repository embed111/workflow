#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_acceptance_role_creation_browser import (  # type: ignore
    api_request,
    assert_true,
    find_edge,
    edge_dom,
    prepare_runtime_root,
    record_api,
    role_message_text,
    running_server,
    wait_for_health,
    wait_for_role_creation_idle,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Acceptance for role-creation async message batching and delete behavior."
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8144)
    parser.add_argument("--artifacts-dir", default=os.getenv("TEST_ARTIFACTS_DIR") or ".test/evidence")
    parser.add_argument("--logs-dir", default=os.getenv("TEST_LOG_DIR") or ".test/evidence")
    return parser.parse_args()


def capture_dom(edge_path: Path, base_url: str, evidence_root: Path, name: str, session_id: str) -> str:
    query = urlencode(
        {
            "tc_probe": "1",
            "tc_probe_case": "rc_default",
            "tc_probe_session": session_id,
            "_ts": str(int(time.time() * 1000)),
        }
    )
    dom_text = edge_dom(
        edge_path,
        base_url.rstrip("/") + "/?" + query,
        profile_dir=evidence_root / "edge-profile" / name,
    )
    out_path = evidence_root / "dom" / f"{name}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(dom_text, encoding="utf-8")
    return out_path.as_posix()


def task_ids_from_detail(detail: dict) -> list[str]:
    node_ids: list[str] = []
    for stage in list(detail.get("stages") or []):
        for task in list(stage.get("active_tasks") or []):
            node_id = str(task.get("node_id") or "").strip()
            if node_id:
                node_ids.append(node_id)
    return node_ids


def main() -> int:
    args = parse_args()
    repo_root = Path(args.root).resolve()
    run_key = datetime.now().strftime("%Y%m%d-%H%M%S")
    artifacts_dir = Path(args.artifacts_dir).resolve()
    logs_dir = Path(args.logs_dir).resolve()
    evidence_root = artifacts_dir / f"role-creation-async-delete-{run_key}"
    log_root = logs_dir / f"role-creation-async-delete-{run_key}"
    api_dir = evidence_root / "api"
    evidence_root.mkdir(parents=True, exist_ok=True)
    api_dir.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    runtime_base = Path(os.getenv("TEST_TMP_DIR") or (repo_root / ".test" / "runtime")).resolve()
    runtime_root = prepare_runtime_root(repo_root, runtime_base / "role-creation-async-delete")
    base_url = f"http://{args.host}:{args.port}"
    edge_path = find_edge()

    sys.path.insert(0, str(repo_root / "src"))
    from workflow_app.server.bootstrap import web_server_runtime as ws  # type: ignore
    from workflow_app.server.infra.db.migrations import ensure_tables  # type: ignore

    ensure_tables(runtime_root)
    ws.bind_training_center_runtime_once()

    evidence: dict = {
        "repo_root": str(repo_root),
        "runtime_root": str(runtime_root),
        "base_url": base_url,
        "edge_path": str(edge_path),
        "api": {},
        "dom": {},
        "assertions": {},
    }
    operator = "role-creation-async-delete-acceptance"

    try:
        with running_server(
            repo_root,
            runtime_root,
            host=args.host,
            port=args.port,
            stdout_path=log_root / "server.stdout.log",
            stderr_path=log_root / "server.stderr.log",
        ):
            evidence["healthz"] = wait_for_health(base_url)

            agent_root = (runtime_root / "workspace-root").resolve()
            artifact_root = (evidence_root / "task-output").resolve()
            (agent_root / "workflow").mkdir(parents=True, exist_ok=True)
            artifact_root.mkdir(parents=True, exist_ok=True)

            status, body = api_request(
                base_url,
                "POST",
                "/api/config/agent-search-root",
                {"agent_search_root": agent_root.as_posix()},
            )
            assert_true(status == 200 and isinstance(body, dict) and body.get("ok"), "switch agent root failed")
            evidence["api"]["switch_agent_root"] = record_api(
                api_dir,
                stage="setup",
                name="switch_agent_root",
                method="POST",
                path="/api/config/agent-search-root",
                payload={"agent_search_root": agent_root.as_posix()},
                status=status,
                body=body,
            )

            status, body = api_request(
                base_url,
                "POST",
                "/api/config/artifact-root",
                {"artifact_root": artifact_root.as_posix()},
            )
            assert_true(status == 200 and isinstance(body, dict) and body.get("ok"), "switch artifact root failed")
            evidence["api"]["switch_artifact_root"] = record_api(
                api_dir,
                stage="setup",
                name="switch_artifact_root",
                method="POST",
                path="/api/config/artifact-root",
                payload={"artifact_root": artifact_root.as_posix()},
                status=status,
                body=body,
            )

            draft_payload = {"session_title": "AsyncDelete Draft", "operator": operator}
            status, draft_create = api_request(base_url, "POST", "/api/training/role-creation/sessions", draft_payload)
            assert_true(status == 200 and isinstance(draft_create, dict) and draft_create.get("ok"), "draft create failed")
            draft_session_id = str((draft_create.get("session") or {}).get("session_id") or "").strip()
            evidence["api"]["draft_create"] = record_api(
                api_dir,
                stage="draft",
                name="create_session",
                method="POST",
                path="/api/training/role-creation/sessions",
                payload=draft_payload,
                status=status,
                body=draft_create,
            )

            draft_dom_path = capture_dom(edge_path, base_url, evidence_root, "draft-delete-visible", draft_session_id)
            evidence["dom"]["draft_delete_visible"] = draft_dom_path
            draft_dom_text = Path(draft_dom_path).read_text(encoding="utf-8")
            assert_true(
                f"data-rc-delete-session=\"{draft_session_id}\"" in draft_dom_text
                or f"data-rc-delete-session='{draft_session_id}'" in draft_dom_text,
                "draft delete button missing in DOM",
            )

            status, draft_delete = api_request(
                base_url,
                "DELETE",
                f"/api/training/role-creation/sessions/{draft_session_id}",
                {"operator": operator},
            )
            assert_true(status == 200 and isinstance(draft_delete, dict) and draft_delete.get("ok"), "draft delete failed")
            evidence["api"]["draft_delete"] = record_api(
                api_dir,
                stage="draft",
                name="delete_session",
                method="DELETE",
                path=f"/api/training/role-creation/sessions/{draft_session_id}",
                payload={"operator": operator},
                status=status,
                body=draft_delete,
            )

            async_payload = {"session_title": "AsyncDelete Batch", "operator": operator}
            status, async_create = api_request(base_url, "POST", "/api/training/role-creation/sessions", async_payload)
            assert_true(status == 200 and isinstance(async_create, dict) and async_create.get("ok"), "async create failed")
            async_session_id = str((async_create.get("session") or {}).get("session_id") or "").strip()
            evidence["api"]["async_create"] = record_api(
                api_dir,
                stage="async",
                name="create_session",
                method="POST",
                path="/api/training/role-creation/sessions",
                payload=async_payload,
                status=status,
                body=async_create,
            )

            timings: list[float] = []
            async_responses: list[dict] = []
            for index, content in enumerate(
                [
                    "先记住角色名是异步验收草稿。",
                    "再补充职责边界和工作方式，连续消息要合并处理。",
                ],
                start=1,
            ):
                message_payload = {
                    "content": content,
                    "operator": operator,
                    "client_message_id": f"async-delete-{index}",
                }
                started_at = time.perf_counter()
                status, async_message = api_request(
                    base_url,
                    "POST",
                    f"/api/training/role-creation/sessions/{async_session_id}/messages",
                    message_payload,
                )
                timings.append(time.perf_counter() - started_at)
                assert_true(
                    status == 200 and isinstance(async_message, dict) and async_message.get("ok"),
                    f"async message {index} failed",
                )
                async_responses.append(async_message)
                evidence["api"][f"async_message_{index}"] = record_api(
                    api_dir,
                    stage="async",
                    name=f"message_{index}",
                    method="POST",
                    path=f"/api/training/role-creation/sessions/{async_session_id}/messages",
                    payload=message_payload,
                    status=status,
                    body=async_message,
                )

            second_session = dict(async_responses[-1].get("session") or {})
            assert_true(
                str(second_session.get("message_processing_status") or "").strip().lower() in {"pending", "running"},
                "async session should be pending or running after second message",
            )
            assert_true(
                int(second_session.get("unhandled_user_message_count") or 0) >= 2,
                "async session should report at least two unhandled messages after second post",
            )

            status, blocked_delete = api_request(
                base_url,
                "DELETE",
                f"/api/training/role-creation/sessions/{async_session_id}",
                {"operator": operator},
            )
            assert_true(
                status == 409
                and isinstance(blocked_delete, dict)
                and str(blocked_delete.get("code") or "").strip() == "role_creation_delete_processing_blocked",
                "processing delete should be blocked",
            )
            evidence["api"]["async_delete_blocked"] = record_api(
                api_dir,
                stage="async",
                name="delete_processing_blocked",
                method="DELETE",
                path=f"/api/training/role-creation/sessions/{async_session_id}",
                payload={"operator": operator},
                status=status,
                body=blocked_delete,
            )

            async_idle = wait_for_role_creation_idle(base_url, async_session_id)
            evidence["api"]["async_idle"] = record_api(
                api_dir,
                stage="async",
                name="idle_detail",
                method="GET",
                path=f"/api/training/role-creation/sessions/{async_session_id}",
                payload=None,
                status=200,
                body=async_idle,
            )
            async_messages = list(async_idle.get("messages") or [])
            async_user_rows = [m for m in async_messages if str(m.get("role") or "").strip().lower() == "user"]
            async_processed_users = [
                m
                for m in async_user_rows
                if str(m.get("processing_state") or (m.get("meta") or {}).get("processing_state") or "").strip().lower()
                == "processed"
            ]
            async_assistant_rows = [
                m
                for m in async_messages
                if str(m.get("role") or "").strip().lower() == "assistant"
                and str(m.get("message_type") or "chat").strip().lower() == "chat"
            ]
            assert_true(len(async_processed_users) >= 2, "async user messages should end as processed")
            assert_true(len(async_assistant_rows) == 2, "async flow should keep welcome + one merged assistant reply")

            creating_payload = {"session_title": "AsyncDelete Creating", "operator": operator}
            status, creating_create = api_request(base_url, "POST", "/api/training/role-creation/sessions", creating_payload)
            assert_true(status == 200 and isinstance(creating_create, dict) and creating_create.get("ok"), "creating create failed")
            creating_session_id = str((creating_create.get("session") or {}).get("session_id") or "").strip()
            evidence["api"]["creating_create"] = record_api(
                api_dir,
                stage="creating",
                name="create_session",
                method="POST",
                path="/api/training/role-creation/sessions",
                payload=creating_payload,
                status=status,
                body=creating_create,
            )

            creating_message_payload = {
                "content": role_message_text("Async Delete Acceptance Role"),
                "operator": operator,
                "client_message_id": "creating-role-spec",
            }
            status, creating_message = api_request(
                base_url,
                "POST",
                f"/api/training/role-creation/sessions/{creating_session_id}/messages",
                creating_message_payload,
            )
            assert_true(
                status == 200 and isinstance(creating_message, dict) and creating_message.get("ok"),
                "creating role-spec message failed",
            )
            evidence["api"]["creating_message"] = record_api(
                api_dir,
                stage="creating",
                name="message",
                method="POST",
                path=f"/api/training/role-creation/sessions/{creating_session_id}/messages",
                payload=creating_message_payload,
                status=status,
                body=creating_message,
            )

            creating_ready = wait_for_role_creation_idle(base_url, creating_session_id)
            evidence["api"]["creating_idle"] = record_api(
                api_dir,
                stage="creating",
                name="idle_detail",
                method="GET",
                path=f"/api/training/role-creation/sessions/{creating_session_id}",
                payload=None,
                status=200,
                body=creating_ready,
            )

            status, creating_start = api_request(
                base_url,
                "POST",
                f"/api/training/role-creation/sessions/{creating_session_id}/start",
                {"operator": operator},
            )
            assert_true(status == 200 and isinstance(creating_start, dict) and creating_start.get("ok"), "creating start failed")
            creating_session = dict(creating_start.get("session") or {})
            creating_ticket_id = str(
                creating_session.get("assignment_ticket_id")
                or (creating_start.get("stage_meta") or {}).get("ticket_id")
                or ""
            ).strip()
            assert_true(
                str(creating_session.get("status") or "").strip().lower() == "creating" and creating_ticket_id,
                "creating session should enter creating with ticket",
            )
            evidence["api"]["creating_start"] = record_api(
                api_dir,
                stage="creating",
                name="start_session",
                method="POST",
                path=f"/api/training/role-creation/sessions/{creating_session_id}/start",
                payload={"operator": operator},
                status=status,
                body=creating_start,
            )

            status, creating_delete_blocked = api_request(
                base_url,
                "DELETE",
                f"/api/training/role-creation/sessions/{creating_session_id}",
                {"operator": operator},
            )
            assert_true(
                status == 409
                and isinstance(creating_delete_blocked, dict)
                and str(creating_delete_blocked.get("code") or "").strip() == "role_creation_delete_creating_blocked",
                "creating delete should be blocked",
            )
            evidence["api"]["creating_delete_blocked"] = record_api(
                api_dir,
                stage="creating",
                name="delete_creating_blocked",
                method="DELETE",
                path=f"/api/training/role-creation/sessions/{creating_session_id}",
                payload={"operator": operator},
                status=status,
                body=creating_delete_blocked,
            )

            creating_dom_path = capture_dom(edge_path, base_url, evidence_root, "creating-delete-hidden", creating_session_id)
            evidence["dom"]["creating_delete_hidden"] = creating_dom_path
            creating_dom_text = Path(creating_dom_path).read_text(encoding="utf-8")
            assert_true(
                f"data-rc-delete-session=\"{creating_session_id}\"" not in creating_dom_text
                and f"data-rc-delete-session='{creating_session_id}'" not in creating_dom_text,
                "creating session should not expose delete button in DOM",
            )

            creating_detail = ws.get_role_creation_session_detail(runtime_root, creating_session_id)
            creating_task_ids = task_ids_from_detail(creating_detail)
            assert_true(bool(creating_task_ids), "creating session task ids missing")
            for node_id in creating_task_ids:
                ws.deliver_assignment_artifact(
                    runtime_root,
                    ticket_id_text=creating_ticket_id,
                    node_id_text=node_id,
                    operator=operator,
                    artifact_label=f"{node_id}.html",
                    delivery_note="async delete acceptance delivered",
                )
                ws.override_assignment_node_status(
                    runtime_root,
                    ticket_id_text=creating_ticket_id,
                    node_id_text=node_id,
                    target_status="succeeded",
                    operator=operator,
                    reason="async delete acceptance completed",
                    result_ref=f"acceptance://{node_id}",
                )

            complete_payload = {
                "operator": operator,
                "confirmed": True,
                "acceptance_note": "all starter tasks completed in acceptance harness",
            }
            status, completed = api_request(
                base_url,
                "POST",
                f"/api/training/role-creation/sessions/{creating_session_id}/complete",
                complete_payload,
            )
            assert_true(status == 200 and isinstance(completed, dict) and completed.get("ok"), "complete session failed")
            completed_session = dict(completed.get("session") or {})
            assert_true(
                str(completed_session.get("status") or "").strip().lower() == "completed",
                "session should become completed",
            )
            evidence["api"]["completed_session"] = record_api(
                api_dir,
                stage="completed",
                name="complete_session",
                method="POST",
                path=f"/api/training/role-creation/sessions/{creating_session_id}/complete",
                payload=complete_payload,
                status=status,
                body=completed,
            )

            completed_dom_path = capture_dom(edge_path, base_url, evidence_root, "completed-delete-visible", creating_session_id)
            evidence["dom"]["completed_delete_visible"] = completed_dom_path
            completed_dom_text = Path(completed_dom_path).read_text(encoding="utf-8")
            assert_true(
                f"data-rc-delete-session=\"{creating_session_id}\"" in completed_dom_text
                or f"data-rc-delete-session='{creating_session_id}'" in completed_dom_text,
                "completed session should expose delete button in DOM",
            )

            status, completed_delete = api_request(
                base_url,
                "DELETE",
                f"/api/training/role-creation/sessions/{creating_session_id}",
                {"operator": operator},
            )
            assert_true(
                status == 200 and isinstance(completed_delete, dict) and completed_delete.get("ok"),
                "completed delete failed",
            )
            evidence["api"]["completed_delete"] = record_api(
                api_dir,
                stage="completed",
                name="delete_session",
                method="DELETE",
                path=f"/api/training/role-creation/sessions/{creating_session_id}",
                payload={"operator": operator},
                status=status,
                body=completed_delete,
            )

            evidence["assertions"] = {
                "async_post_latencies_ms": [round(item * 1000, 1) for item in timings],
                "async_unhandled_after_second_post": int(second_session.get("unhandled_user_message_count") or 0),
                "async_final_user_processed_count": len(async_processed_users),
                "async_final_assistant_chat_count": len(async_assistant_rows),
                "creating_task_count": len(creating_task_ids),
                "draft_session_id": draft_session_id,
                "async_session_id": async_session_id,
                "creating_session_id": creating_session_id,
                "creating_ticket_id": creating_ticket_id,
            }

            summary_md = evidence_root / "summary.md"
            summary_md.write_text(
                "\n".join(
                    [
                        "# Role Creation Async/Delete Acceptance",
                        "",
                        f"- base_url: {base_url}",
                        f"- runtime_root: {runtime_root.as_posix()}",
                        f"- edge_path: {edge_path.as_posix()}",
                        f"- artifact_root: {artifact_root.as_posix()}",
                        "",
                        "## Checks",
                        "",
                        f"- draft delete visible in DOM and API delete succeeds: session `{draft_session_id}`",
                        f"- async batching returns quickly, delete blocked during processing, then settles idle: session `{async_session_id}`",
                        f"- creating session hides delete in DOM and blocks delete API, completed session shows delete and can be removed: session `{creating_session_id}`",
                        "",
                        "## Evidence",
                        "",
                        f"- api_dir: {api_dir.as_posix()}",
                        f"- draft_dom: {draft_dom_path}",
                        f"- creating_dom: {creating_dom_path}",
                        f"- completed_dom: {completed_dom_path}",
                        f"- server_stdout: {(log_root / 'server.stdout.log').as_posix()}",
                        f"- server_stderr: {(log_root / 'server.stderr.log').as_posix()}",
                        "",
                        "## Metrics",
                        "",
                        f"- async_post_latencies_ms: {evidence['assertions']['async_post_latencies_ms']}",
                        f"- async_unhandled_after_second_post: {evidence['assertions']['async_unhandled_after_second_post']}",
                        f"- async_final_user_processed_count: {evidence['assertions']['async_final_user_processed_count']}",
                        f"- async_final_assistant_chat_count: {evidence['assertions']['async_final_assistant_chat_count']}",
                        f"- creating_task_count: {evidence['assertions']['creating_task_count']}",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            evidence["summary_md"] = summary_md.as_posix()
            evidence["ok"] = True
    finally:
        write_json(evidence_root / "summary.json", evidence)

    print((evidence_root / "summary.md").as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
