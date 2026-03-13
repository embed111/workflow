#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import socket
import sqlite3
import subprocess
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def call(
    base_url: str,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    *,
    timeout_s: int = 60,
) -> tuple[int, dict[str, Any]]:
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url=base_url + path, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=max(10, int(timeout_s))) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, (json.loads(body) if body else {})
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            payload_obj = json.loads(body) if body else {}
        except Exception:
            payload_obj = {"raw": body}
        return exc.code, payload_obj


def call_many(
    base_url: str, method: str, path: str, *, count: int, timeout_s: int = 60
) -> list[tuple[int, dict[str, Any]]]:
    with ThreadPoolExecutor(max_workers=max(1, int(count))) as pool:
        futures = [
            pool.submit(call, base_url, method, path, None, timeout_s=int(timeout_s))
            for _ in range(max(1, int(count)))
        ]
        return [future.result() for future in futures]


def wait_health(base_url: str, timeout_s: int = 60) -> None:
    end_at = time.time() + timeout_s
    while time.time() < end_at:
        st, payload = call(base_url, "GET", "/healthz", None, timeout_s=10)
        if st == 200 and bool(payload.get("ok")):
            return
        time.sleep(0.5)
    raise RuntimeError("healthz timeout")


def find_edge() -> Path:
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    raise RuntimeError("msedge not found")


def edge_shot(
    edge_path: Path,
    url: str,
    shot_path: Path,
    *,
    width: int = 1440,
    height: int = 980,
    budget_ms: int = 20000,
) -> None:
    shot_path.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for _attempt in range(3):
        profile_dir = shot_path.parent / ".edge_profile" / f"shot-{uuid.uuid4().hex}"
        profile_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            str(edge_path),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={profile_dir.as_posix()}",
            f"--window-size={int(width)},{int(height)}",
            f"--virtual-time-budget={max(1000, int(budget_ms))}",
            f"--screenshot={shot_path.as_posix()}",
            url,
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=180)
            if proc.returncode != 0:
                raise RuntimeError(f"edge screenshot failed: {proc.stderr}")
            return
        except Exception as exc:
            last_error = exc
            time.sleep(1.0)
        finally:
            # Avoid cross-shot profile locking / process residue.
            try:
                import shutil

                shutil.rmtree(profile_dir, ignore_errors=True)
            except Exception:
                pass
    if last_error is not None:
        raise last_error


def pick_port(host: str, start_port: int = 18090, attempts: int = 40) -> int:
    for port in range(int(start_port), int(start_port) + int(attempts)):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, int(port)))
            except OSError:
                continue
            return int(port)
    raise RuntimeError("no free port available")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pick_training_agent(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    rows = [row for row in items if isinstance(row, dict)]
    if not rows:
        return None
    for preferred_id in ("Analyst2",):
        for row in rows:
            if str(row.get("agent_id") or "").strip() == preferred_id:
                return row
    for row in rows:
        if str(row.get("agent_id") or "").strip() != "Analyst":
            return row
    return rows[0]


def dump_audit_log(db_path: Path, *, loop_id: str) -> list[dict[str, Any]]:
    conn = sqlite3.connect(db_path.as_posix())
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT audit_id,action,operator,target_id,detail_json,created_at
            FROM training_audit_log
            WHERE target_id=?
              AND action IN ('enter-next-round','rollback-round-increment')
            ORDER BY created_at DESC
            LIMIT 50
            """,
            (loop_id,),
        ).fetchall()
    finally:
        conn.close()
    items: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        record = {k: row[k] for k in row.keys()}
        record["_row_index"] = idx + 1
        items.append(record)
    return items


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0, help="0 means auto-pick a free port")
    parser.add_argument("--budget-ms", type=int, default=22000)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    evidence_root = repo_root / "logs" / "runs" / f"tc-loop-evolution-{ts}"
    shots_dir = evidence_root / "screenshots"
    api_dir = evidence_root / "api"
    runtime_root = repo_root / ".runtime"
    db_path = runtime_root / "state" / "workflow.db"
    evidence_root.mkdir(parents=True, exist_ok=True)
    shots_dir.mkdir(parents=True, exist_ok=True)
    api_dir.mkdir(parents=True, exist_ok=True)

    host = str(args.host)
    port = int(args.port) if int(args.port) > 0 else pick_port(host)
    base_url = f"http://{host}:{port}"

    server_stdout = evidence_root / "server_stdout.log"
    server_stderr = evidence_root / "server_stderr.log"
    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "workflow_web_server.py"),
        "--host",
        host,
        "--port",
        str(port),
        "--root",
        runtime_root.as_posix(),
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=repo_root.as_posix(),
        stdout=server_stdout.open("w", encoding="utf-8"),
        stderr=server_stderr.open("w", encoding="utf-8"),
    )
    try:
        wait_health(base_url, timeout_s=80)

        # Reproduce-protection: concurrent GET should not crash with "database is locked".
        agents_responses = call_many(base_url, "GET", "/api/training/agents", count=4, timeout_s=60)
        api_dir.joinpath("concurrent_training_agents.json").write_text(
            json.dumps({"base_url": base_url, "responses": agents_responses}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        st_agents, agents_payload = call(base_url, "GET", "/api/training/agents?include_test_data=0", None, timeout_s=90)
        if st_agents != 200 or not bool(agents_payload.get("ok")):
            raise RuntimeError(f"list agents failed: status={st_agents}")
        agents_items = agents_payload.get("items") if isinstance(agents_payload, dict) else []
        if not isinstance(agents_items, list) or not agents_items:
            raise RuntimeError("no training agents available")
        pick = pick_training_agent(agents_items)
        target_agent_id = str((pick or {}).get("agent_id") or "").strip()
        if not target_agent_id:
            raise RuntimeError("agent_id missing")

        goal = f"tc-loop-evidence {ts}"
        plan_payload = {
            "target_agent_id": target_agent_id,
            "capability_goal": goal,
            "training_tasks": [f"loop task {ts} 1", f"loop task {ts} 2"],
            "acceptance_criteria": f"acceptance {ts}",
            "priority": "P0",
            "execution_engine": "workflow_native",
            "operator": "acceptance-script",
            "created_by": "acceptance-script",
        }
        st_plan, plan_resp = call(base_url, "POST", "/api/training/plans/manual", plan_payload, timeout_s=90)
        if st_plan != 200 or not bool(plan_resp.get("ok")):
            raise RuntimeError(f"create plan failed: status={st_plan}, payload={plan_resp}")
        write_json(api_dir / "create_plan.json", plan_resp)
        queue_task_id = str(plan_resp.get("queue_task_id") or "").strip()
        if not queue_task_id:
            raise RuntimeError("queue_task_id missing")

        st_loop0, loop0 = call(base_url, "GET", f"/api/training/queue/{queue_task_id}/loop", None, timeout_s=90)
        if st_loop0 != 200 or not bool(loop0.get("ok")):
            raise RuntimeError(f"get loop failed: status={st_loop0}, payload={loop0}")
        write_json(api_dir / "loop_before.json", loop0)
        loop_id = str(loop0.get("loop_id") or "").strip()
        current_node_id = str(loop0.get("current_node_id") or "").strip()
        if not loop_id:
            raise RuntimeError("loop_id missing")

        st_q0, q0 = call(base_url, "GET", "/api/training/queue?include_removed=1&include_test_data=0", None, timeout_s=90)
        if st_q0 != 200 or not bool(q0.get("ok")):
            raise RuntimeError(f"list queue failed: status={st_q0}, payload={q0}")
        items0 = q0.get("items") if isinstance(q0, dict) else []
        matched0 = [row for row in items0 if isinstance(row, dict) and str(row.get("capability_goal") or "").strip() == goal]
        if len(matched0) < 1:
            raise RuntimeError("queue does not contain created plan")

        edge = find_edge()

        def url_for(params: dict[str, str]) -> str:
            return base_url + "/?" + urlencode(params)

        base_status_params = {
            "tc_loop_mode": "status",
            "tc_loop_tab": "score",
            "tc_loop_task": queue_task_id,
            "tc_loop_node": current_node_id or queue_task_id,
            "tc_loop_search": goal,
        }

        shots: list[tuple[str, str, dict[str, str], dict[str, Any]]] = [
            (
                "01_status_steps.png",
                "任务状态-顶部五阶段流",
                dict(base_status_params),
                {"width": 1440, "height": 980},
            ),
            (
                "02_status_graph.png",
                "任务状态-演进图(真实数据或空态)",
                dict(base_status_params),
                {"width": 1440, "height": 980},
            ),
            (
                "03_status_right_pane.png",
                "任务状态-右侧当前节点详情",
                dict(base_status_params),
                {"width": 1440, "height": 980},
            ),
            (
                "04_create_steps.png",
                "创建任务-顶部五阶段流",
                {"tc_loop_mode": "create"},
                {"width": 1440, "height": 980},
            ),
            (
                "05_create_path_preview.png",
                "创建任务-训练路径预览(劣化回退/提升不足进下一轮)",
                {"tc_loop_mode": "create"},
                {"width": 1440, "height": 980},
            ),
            (
                "06_scrollbars_bottom_alignment.png",
                "区内滚动条与底边平齐",
                {"tc_loop_mode": "create"},
                {"width": 1440, "height": 760},
            ),
        ]

        created: list[dict[str, str]] = []
        for filename, title, params, shot_cfg in shots:
            shot_path = shots_dir / filename
            edge_shot(
                edge,
                url_for(params),
                shot_path,
                width=int(shot_cfg.get("width", 1440)),
                height=int(shot_cfg.get("height", 980)),
                budget_ms=int(args.budget_ms),
            )
            created.append({"title": title, "path": shot_path.resolve().as_posix(), "url": url_for(params)})

        st_enter, enter_resp = call(
            base_url,
            "POST",
            f"/api/training/queue/{queue_task_id}/loop/enter-next-round",
            {"operator": "acceptance-script", "reason": "enter-next-round evidence"},
            timeout_s=90,
        )
        if st_enter != 200 or not bool(enter_resp.get("ok")):
            raise RuntimeError(f"enter-next-round failed: status={st_enter}, payload={enter_resp}")
        write_json(api_dir / "enter_next_round.json", enter_resp)
        created_queue_task_id = str(enter_resp.get("created_queue_task_id") or "").strip()
        if not created_queue_task_id:
            raise RuntimeError("created_queue_task_id missing")

        st_loop1, loop1 = call(base_url, "GET", f"/api/training/queue/{created_queue_task_id}/loop", None, timeout_s=90)
        if st_loop1 != 200 or not bool(loop1.get("ok")):
            raise RuntimeError(f"get loop after enter failed: status={st_loop1}, payload={loop1}")
        write_json(api_dir / "loop_after_enter.json", loop1)
        loop_current_1 = str(loop1.get("current_node_id") or "").strip()
        if loop_current_1 != created_queue_task_id:
            raise RuntimeError("loop current_node_id not advanced after enter-next-round")

        st_q1, q1 = call(base_url, "GET", "/api/training/queue?include_removed=1&include_test_data=0", None, timeout_s=90)
        if st_q1 != 200 or not bool(q1.get("ok")):
            raise RuntimeError(f"list queue after enter failed: status={st_q1}, payload={q1}")
        items1 = q1.get("items") if isinstance(q1, dict) else []
        matched1 = [row for row in items1 if isinstance(row, dict) and str(row.get("capability_goal") or "").strip() == goal]
        if len(matched1) < 2:
            raise RuntimeError("queue did not change after enter-next-round")

        shot7 = shots_dir / "07_after_enter_next_round.png"
        params7 = {
            "tc_loop_mode": "status",
            "tc_loop_tab": "score",
            "tc_loop_task": created_queue_task_id,
            "tc_loop_node": loop_current_1 or created_queue_task_id,
            "tc_loop_search": goal,
        }
        edge_shot(edge, url_for(params7), shot7, width=1440, height=980, budget_ms=int(args.budget_ms))
        created.append({"title": "进入下一轮后-演进图与队列变化", "path": shot7.resolve().as_posix(), "url": url_for(params7)})

        st_rb, rb_resp = call(
            base_url,
            "POST",
            f"/api/training/queue/{created_queue_task_id}/loop/rollback-round-increment",
            {"operator": "acceptance-script", "reason": "rollback evidence"},
            timeout_s=90,
        )
        if st_rb != 200 or not bool(rb_resp.get("ok")):
            raise RuntimeError(f"rollback-round-increment failed: status={st_rb}, payload={rb_resp}")
        write_json(api_dir / "rollback_round_increment.json", rb_resp)
        rb_node_id = str(rb_resp.get("rollback_node_id") or rb_resp.get("current_node_id") or "").strip()

        st_loop2, loop2 = call(base_url, "GET", f"/api/training/queue/{created_queue_task_id}/loop", None, timeout_s=90)
        if st_loop2 != 200 or not bool(loop2.get("ok")):
            raise RuntimeError(f"get loop after rollback failed: status={st_loop2}, payload={loop2}")
        write_json(api_dir / "loop_after_rollback.json", loop2)
        if rb_node_id and str(loop2.get("current_node_id") or "").strip() != rb_node_id:
            raise RuntimeError("loop current_node_id not updated after rollback-round-increment")

        shot8 = shots_dir / "08_after_rollback_round_increment.png"
        params8 = {
            "tc_loop_mode": "status",
            "tc_loop_tab": "decision",
            "tc_loop_task": created_queue_task_id,
            "tc_loop_node": rb_node_id or str(loop2.get("current_node_id") or "").strip(),
            "tc_loop_search": goal,
        }
        edge_shot(edge, url_for(params8), shot8, width=1440, height=980, budget_ms=int(args.budget_ms))
        created.append({"title": "回退本轮新增后-演进图与右侧面板", "path": shot8.resolve().as_posix(), "url": url_for(params8)})

        audit_rows = dump_audit_log(db_path, loop_id=loop_id)
        if len(audit_rows) < 2:
            raise RuntimeError("audit log missing enter-next-round / rollback-round-increment records")
        write_json(api_dir / "training_audit_log_loop_actions.json", {"loop_id": loop_id, "rows": audit_rows})

        summary_md = evidence_root / "summary.md"
        lines = [
            f"# Training Loop Evidence ({ts})",
            "",
            f"- base_url: {base_url}",
            f"- db_path: {db_path.as_posix()}",
            f"- server_stdout: {server_stdout.as_posix()}",
            f"- server_stderr: {server_stderr.as_posix()}",
            "",
            "## API",
            f"- concurrent_agents: {(api_dir / 'concurrent_training_agents.json').as_posix()}",
            f"- create_plan: {(api_dir / 'create_plan.json').as_posix()}",
            f"- loop_before: {(api_dir / 'loop_before.json').as_posix()}",
            f"- enter_next_round: {(api_dir / 'enter_next_round.json').as_posix()}",
            f"- loop_after_enter: {(api_dir / 'loop_after_enter.json').as_posix()}",
            f"- rollback_round_increment: {(api_dir / 'rollback_round_increment.json').as_posix()}",
            f"- loop_after_rollback: {(api_dir / 'loop_after_rollback.json').as_posix()}",
            f"- training_audit_log: {(api_dir / 'training_audit_log_loop_actions.json').as_posix() if loop_id else ''}",
            "",
            "## Screenshots",
            "",
        ]
        for item in created:
            lines.append(f"- {item['title']}: {item['path']}")
            lines.append(f"  url: {item['url']}")
        summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

        print(summary_md.as_posix())
        ok = (
            all(Path(item["path"]).exists() for item in created)
            and all(int(st) == 200 for st, _ in agents_responses)
            and bool(loop_id)
            and bool(audit_rows)
        )
        return 0 if ok else 1
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
