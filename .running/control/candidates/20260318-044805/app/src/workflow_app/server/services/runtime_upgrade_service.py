from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any


RUNTIME_ENV_VAR = "WORKFLOW_RUNTIME_ENV"
RUNTIME_SOURCE_ROOT_VAR = "WORKFLOW_RUNTIME_SOURCE_ROOT"
RUNTIME_CONTROL_ROOT_VAR = "WORKFLOW_RUNTIME_CONTROL_ROOT"
RUNTIME_MANIFEST_PATH_VAR = "WORKFLOW_RUNTIME_MANIFEST_PATH"
RUNTIME_DEPLOY_ROOT_VAR = "WORKFLOW_RUNTIME_DEPLOY_ROOT"
RUNTIME_VERSION_VAR = "WORKFLOW_RUNTIME_VERSION"
RUNTIME_PID_FILE_VAR = "WORKFLOW_RUNTIME_PID_FILE"
RUNTIME_INSTANCE_FILE_VAR = "WORKFLOW_RUNTIME_INSTANCE_FILE"

PROD_UPGRADE_EXIT_CODE = 73


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _remove_file(path: Path | None) -> None:
    if not isinstance(path, Path):
        return
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except Exception:
        return


def _env_path(name: str) -> Path | None:
    text = str(os.getenv(name) or "").strip()
    if not text:
        return None
    return Path(text).resolve(strict=False)


def _version_rank(value: dict[str, Any]) -> str:
    return str(value.get("version_rank") or value.get("current_version_rank") or value.get("version") or value.get("current_version") or "").strip()


def current_runtime_environment() -> str:
    text = str(os.getenv(RUNTIME_ENV_VAR) or "").strip().lower()
    return text or "source"


def current_runtime_source_root() -> Path | None:
    return _env_path(RUNTIME_SOURCE_ROOT_VAR)


def current_runtime_control_root() -> Path | None:
    env_path = _env_path(RUNTIME_CONTROL_ROOT_VAR)
    if isinstance(env_path, Path):
        return env_path
    deploy_root = _env_path(RUNTIME_DEPLOY_ROOT_VAR)
    if isinstance(deploy_root, Path) and deploy_root.parent.name == ".running":
        return (deploy_root.parent / "control").resolve(strict=False)
    return None


def current_runtime_manifest_path() -> Path | None:
    env_path = _env_path(RUNTIME_MANIFEST_PATH_VAR)
    if isinstance(env_path, Path):
        return env_path
    control_root = current_runtime_control_root()
    environment = current_runtime_environment()
    if isinstance(control_root, Path) and environment:
        return (control_root / "envs" / f"{environment}.json").resolve(strict=False)
    return None


def current_runtime_manifest() -> dict[str, Any]:
    path = current_runtime_manifest_path()
    if not isinstance(path, Path):
        return {}
    payload = _read_json(path)
    payload.setdefault("manifest_path", path.as_posix())
    return payload


def prod_candidate_path() -> Path | None:
    control_root = current_runtime_control_root()
    if not isinstance(control_root, Path):
        return None
    return (control_root / "prod-candidate.json").resolve(strict=False)


def prod_last_action_path() -> Path | None:
    control_root = current_runtime_control_root()
    if not isinstance(control_root, Path):
        return None
    return (control_root / "prod-last-action.json").resolve(strict=False)


def prod_upgrade_request_path() -> Path | None:
    control_root = current_runtime_control_root()
    if not isinstance(control_root, Path):
        return None
    return (control_root / "prod-upgrade-request.json").resolve(strict=False)


def read_prod_candidate() -> dict[str, Any]:
    path = prod_candidate_path()
    if not isinstance(path, Path):
        return {}
    payload = _read_json(path)
    payload.setdefault("candidate_record_path", path.as_posix())
    return payload


def read_prod_last_action() -> dict[str, Any]:
    path = prod_last_action_path()
    if not isinstance(path, Path):
        return {}
    return _read_json(path)


def read_prod_upgrade_request() -> dict[str, Any]:
    path = prod_upgrade_request_path()
    if not isinstance(path, Path):
        return {}
    return _read_json(path)


def runtime_snapshot() -> dict[str, Any]:
    manifest = current_runtime_manifest()
    environment = current_runtime_environment()
    current_version = str(os.getenv(RUNTIME_VERSION_VAR) or manifest.get("current_version") or "").strip()
    current_rank = str(manifest.get("current_version_rank") or current_version).strip()
    return {
        "environment": environment,
        "source_root": (current_runtime_source_root() or Path(".")).resolve(strict=False).as_posix()
        if current_runtime_source_root()
        else "",
        "control_root": current_runtime_control_root().as_posix() if current_runtime_control_root() else "",
        "manifest": manifest,
        "manifest_path": str(manifest.get("manifest_path") or ""),
        "current_version": current_version,
        "current_version_rank": current_rank,
        "candidate": read_prod_candidate(),
        "last_action": read_prod_last_action(),
        "upgrade_request": read_prod_upgrade_request(),
    }


def candidate_is_complete(candidate: dict[str, Any]) -> bool:
    evidence_path = str(candidate.get("evidence_path") or "").strip()
    app_root = str(candidate.get("candidate_app_root") or "").strip()
    if not evidence_path or not app_root:
        return False
    return Path(evidence_path).exists() and Path(app_root).exists()


def candidate_is_newer(snapshot: dict[str, Any]) -> bool:
    candidate = dict(snapshot.get("candidate") or {})
    candidate_rank = _version_rank(candidate)
    current_rank = str(snapshot.get("current_version_rank") or "").strip()
    if not candidate_rank or not current_rank:
        return bool(candidate_rank and candidate_is_complete(candidate))
    return candidate_is_complete(candidate) and candidate_rank > current_rank


def build_runtime_upgrade_status(
    snapshot: dict[str, Any],
    *,
    running_task_count: int,
    agent_call_count: int,
) -> dict[str, Any]:
    candidate = dict(snapshot.get("candidate") or {})
    last_action = dict(snapshot.get("last_action") or {})
    request = dict(snapshot.get("upgrade_request") or {})
    environment = str(snapshot.get("environment") or "source")
    is_prod = environment == "prod"
    blocker = ""
    blocker_code = ""
    request_pending = bool(request and str(request.get("candidate_version") or "").strip())
    if running_task_count > 0:
        blocker = "存在运行中任务，暂不可升级"
        blocker_code = "running_tasks_present"
    elif request_pending:
        blocker = "正式升级正在切换中，请等待页面自动重连"
        blocker_code = "upgrade_switching"
    elif is_prod and candidate and not candidate_is_complete(candidate):
        blocker = "升级候选不完整，请先重新生成"
        blocker_code = "candidate_incomplete"
    elif is_prod and not candidate_is_newer(snapshot):
        blocker = "暂无可升级版本"
        blocker_code = "no_candidate"
    return {
        "ok": True,
        "environment": environment,
        "current_version": str(snapshot.get("current_version") or ""),
        "current_version_rank": str(snapshot.get("current_version_rank") or ""),
        "candidate_version": str(candidate.get("version") or ""),
        "candidate_version_rank": _version_rank(candidate),
        "candidate_source_environment": str(candidate.get("source_environment") or ""),
        "candidate_passed_at": str(candidate.get("passed_at") or ""),
        "candidate_evidence_path": str(candidate.get("evidence_path") or ""),
        "candidate_record_path": str(candidate.get("candidate_record_path") or ""),
        "candidate_available": bool(candidate and candidate_is_complete(candidate)),
        "candidate_is_newer": bool(candidate_is_newer(snapshot)),
        "request_pending": request_pending,
        "request_candidate_version": str(request.get("candidate_version") or ""),
        "request_requested_at": str(request.get("requested_at") or ""),
        "running_task_count": max(0, int(running_task_count)),
        "agent_call_count": max(0, int(agent_call_count)),
        "blocking_reason": blocker,
        "blocking_reason_code": blocker_code,
        "can_upgrade": bool(is_prod and not blocker and candidate_is_newer(snapshot)),
        "banner_visible": bool(is_prod and candidate_is_newer(snapshot)),
        "last_action": last_action,
    }


def write_prod_upgrade_request(
    snapshot: dict[str, Any],
    *,
    operator: str,
) -> dict[str, Any]:
    path = prod_upgrade_request_path()
    if not isinstance(path, Path):
        raise RuntimeError("runtime control root unavailable")
    candidate = dict(snapshot.get("candidate") or {})
    payload = {
        "environment": "prod",
        "requested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "requested_by": str(operator or "web-user"),
        "current_version": str(snapshot.get("current_version") or ""),
        "candidate_version": str(candidate.get("version") or ""),
        "candidate_evidence_path": str(candidate.get("evidence_path") or ""),
        "candidate_app_root": str(candidate.get("candidate_app_root") or ""),
    }
    _write_json(path, payload)
    return payload


def schedule_runtime_shutdown(
    state: Any,
    *,
    exit_code: int,
    reason: str,
    delay_seconds: float = 0.25,
) -> None:
    setattr(state, "_runtime_shutdown_code", int(exit_code))
    setattr(state, "_runtime_shutdown_reason", str(reason or ""))

    def _shutdown() -> None:
        if delay_seconds > 0:
            time.sleep(delay_seconds)
        try:
            state.stop_event.set()
        except Exception:
            pass
        shutdown_cb = getattr(state, "_runtime_server_shutdown", None)
        if callable(shutdown_cb):
            try:
                shutdown_cb()
            except Exception:
                return

    thread = threading.Thread(target=_shutdown, name="runtime-upgrade-shutdown", daemon=True)
    thread.start()


def requested_shutdown_code(state: Any) -> int:
    try:
        return int(getattr(state, "_runtime_shutdown_code", 0) or 0)
    except Exception:
        return 0


def runtime_process_start(
    *,
    host: str,
    port: int,
) -> None:
    pid_path = _env_path(RUNTIME_PID_FILE_VAR)
    instance_path = _env_path(RUNTIME_INSTANCE_FILE_VAR)
    runtime_env = current_runtime_environment()
    payload = {
        "environment": runtime_env,
        "version": str(os.getenv(RUNTIME_VERSION_VAR) or "").strip(),
        "pid": os.getpid(),
        "host": str(host or ""),
        "port": int(port or 0),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "running",
    }
    if isinstance(pid_path, Path):
        pid_path.parent.mkdir(parents=True, exist_ok=True)
        pid_path.write_text(str(os.getpid()), encoding="utf-8")
    if isinstance(instance_path, Path):
        _write_json(instance_path, payload)


def runtime_process_stop() -> None:
    pid_path = _env_path(RUNTIME_PID_FILE_VAR)
    instance_path = _env_path(RUNTIME_INSTANCE_FILE_VAR)
    _remove_file(pid_path)
    if isinstance(instance_path, Path):
        current = _read_json(instance_path)
        current["stopped_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        current["status"] = "stopped"
        _write_json(instance_path, current)
