# Prod Idle Upgrade Watcher

- `2026-04-19T13:13:32+08:00` watcher 启动：base_url=http://127.0.0.1:8090, timeout_seconds=1800.0, poll_seconds=10.0, apply_wait_seconds=600.0, operator=codex
- `2026-04-19T13:13:34+08:00` 单次检查状态：current=20260419-112637, candidate=20260419-125500, candidate_is_newer=True, request_pending=False, running_task_count=0, can_upgrade=True, ghost_running_detected=False, ghost_running_count=0
- `2026-04-19T13:13:35+08:00` 单次检查发起 apply：status_code=202 payload={"ok": true, "message": "prod upgrade accepted; page may reconnect shortly", "requested_at": "2026-04-19T05:13:35Z", "current_version": "20260419-112637", "candidate_version": "20260419-125500", "reconnect_hint": "页面会短暂刷新和重连，请等待正式环境完成切换。", "environment": "prod", "current_version_rank": "20260419-112637", "candidate_version_rank": "20260419-125500", "candidate_source_environment": "test", "candidate_passed_at": "2026-04-19T04:55:11.8612979Z", "candidate_evidence_path": "D:\\code\\AI\\J-Agents\\workflow\\.running\\control\\reports\\test-gate-20260419-125500.json", "candidate_record_path": "D:/code/AI/J-Agents/workflow/.running/control/prod-candidate.json", "candidate_available": true, "candidate_is_newer": true, "request_pending": false, "request_candidate_version": "", "request_requested_at": "", "drain_active": true, "drain_reason": "已存在更高 prod candidate，冻结新派发为 idle watcher 创造升级空窗。", "drain_reason_code": "candidate_newer_pending_idle_window", "running_task_count": 0, "agent_call_count": 0, "blocking_reason": "", "blocking_reason_code": "", "can_upgrade": true, "banner_visible": true, "supervisor_attached": true, "supervisor_pid": 39456, "supervisor_kind": "start_workflow_env", "last_action": {"candidate_version": "20260419-112637", "action": "upgrade", "current_version": "20260419-112637", "status": "success", "previous_version": "20260419-095333", "finished_at": "2026-04-19T03:54:23.4677433Z", "evidence_path": "D:\\code\\AI\\J-Agents\\workflow\\.running\\control\\reports\\test-gate-20260419-112637.json"}, "upgrade_highlights": ["任务产物默认按 HTML 生成，任务详情里可以直接打开查看。", "页面交互和展示体验有更新。", "部署与环境切换脚本有更新。"], "running_gate_exclusion_requested": false, "running_gate_exclusion_applied": false, "exclude_assignment_ticket_id": "", "exclude_assignment_node_id": "", "excluded_running_task_count": 0, "ghost_running_detected": false, "ghost_running_count": 0, "ghost_running_refs": []}
- `2026-04-19T13:13:36+08:00` 等待升级完成时状态接口不可用：status_code=0 payload={"ok": false, "error": "[WinError 10054] 远程主机强迫关闭了一个现有的连接。", "code": "request_failed"}
- `2026-04-19T13:13:48+08:00` 等待升级完成时状态接口不可用：status_code=0 payload={"ok": false, "error": "<urlopen error [WinError 10061] 由于目标计算机积极拒绝，无法连接。>", "code": "request_failed"}
- `2026-04-19T13:14:53+08:00` 等待升级完成时状态接口已恢复；上一条不可用累计 5 次（含首次），持续约 64.7s。
- `2026-04-19T13:14:53+08:00` 等待升级完成中：current=20260419-125500, candidate=20260419-125500, candidate_is_newer=False, request_pending=False, running_task_count=0, can_upgrade=False, ghost_running_detected=False, ghost_running_count=0
- `2026-04-19T13:14:53+08:00` prod 已切到目标 candidate，watcher 结束。
- `2026-04-19T13:14:53+08:00` 升级完成后已刷新 PM 当前版本快照：{
  "ok": true,
  "shell_root": "D:/code/AI/J-Agents/workflow",
  "current_version": "20260419-125500",
  "candidate_version": "20260419-125500",
  "candidate_is_newer": false,
  "request_pending": false,
  "drain_active": false,
  "running_task_count": 0,
  "can_upgrade": false,
  "blocking_reason": "暂无可升级版本",
  "snapshot_at": "2026-04-19T13:14:53+08:00",
  "changed_files": [
    "pm/PM当前版本计划.md",
    "pm/versions/V4/版本计划.md"
  ]
}
