# 两项目运行状态复核与恢复

- 时间：`2026-04-27T19:40:35+08:00`
- 操作人：`Codex`
- preference_ref: `state/user-preferences.md`

## 结论
- `prod` 服务已恢复：`/healthz ok=true`，`8090` listener PID=`66084`。
- 正式升级已完成：`current_version=20260427-184256`，`candidate_version=20260427-184256`，`candidate_is_newer=false`，`request_pending=false`，`drain_active=false`，`supervisor_pid=59648`。
- `workflow` 主线已恢复真实执行：`node-sti-20260427-7a51a4b8` / `arun-20260427-193534-92a24e` 从 `starting_pending` 转为 `live_execution`，provider_pid=`65136`，latest_event_at=`2026-04-27T19:40:10+08:00`。
- `project-ai-novel-profit` 已恢复下一棒：`node-sti-20260427-c2420171` 终态为 `succeeded`，已回补 handoff `amh-20260427-193559-53047a`，`[持续迭代] novel_project_pm` 下一次触发为 `2026-04-27T23:36:00+08:00`。
- 现场还有第三个 active 项目 `project-comics-smoke`，`startup_bridge.state=recovered`，未见 ghost running。

## 根因与恢复动作
- `workflow` 19:15 轮次在升级恢复期间卡成假运行，已由 ghost repair 收敛为失败并通过 handoff 续排到 19:35。
- `project-ai-novel-profit` 的 13:48 轮次完成时仍处于旧 `prod` 版本，终态已写回但没有生成 durable handoff；升级完成后不会自动补旧轮次 handoff。
- 已使用当前 `prod=20260427-184256` handoff runtime 回补并 drain 该项目 handoff，恢复下一棒。

## 证据
- `/api/runtime-upgrade/status`：`running_task_count=1`，原因是当前 `workflow` 主线真实运行中；无 ghost running。
- `/api/schedules`：
  - `[持续迭代] workflow`：`last_result_status=running`，`last_result_node_id=node-sti-20260427-7a51a4b8`
  - `[持续迭代] novel_project_pm`：`last_result_status=succeeded`，`next_trigger_at=2026-04-27T23:36:00+08:00`
- `/api/projects`：`workflow`、`project-ai-novel-profit`、`project-comics-smoke` 均为 `lifecycle_state=active`，`runtime_ready=true`，`startup_ready=true`，`manual_pause=false`，`ghost_running_detected=false`。

