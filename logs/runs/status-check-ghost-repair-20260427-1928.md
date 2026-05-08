# Prod Idle Upgrade Watcher

- `2026-04-27T19:28:17+08:00` watcher 启动：base_url=http://127.0.0.1:8090, timeout_seconds=60.0, poll_seconds=10.0, apply_wait_seconds=600.0, operator=status-check-ghost-repair-20260427-1928
- `2026-04-27T19:28:20+08:00` 单次检查状态：current=20260427-184256, candidate=20260427-184256, candidate_is_newer=False, request_pending=False, running_task_count=0, can_upgrade=False, ghost_running_detected=True, ghost_running_count=1
- `2026-04-27T19:28:20+08:00` 检测到假 running：running_node_projected_terminal / asg-20260327-223335-b79f27 / node-sti-20260427-932c4660
- `2026-04-27T19:28:40+08:00` 假 running 自动修复：status_code=0 payload={"ok": false, "error": "timed out", "code": "request_failed"}
- `2026-04-27T19:28:40+08:00` 修复请求未拿到确定响应，进入状态复核窗口 15.0s。
- `2026-04-27T19:28:42+08:00` 修复请求未拿到确定响应，继续复核状态：current=20260427-184256, candidate=20260427-184256, candidate_is_newer=False, request_pending=False, running_task_count=0, can_upgrade=False, ghost_running_detected=False, ghost_running_count=0
- `2026-04-27T19:28:42+08:00` 假 running 修复后状态：current=20260427-184256, candidate=20260427-184256, candidate_is_newer=False, request_pending=False, running_task_count=0, can_upgrade=False, ghost_running_detected=False, ghost_running_count=0
- `2026-04-27T19:28:42+08:00` 当前仍未到可升级空窗，单次检查跳过。
