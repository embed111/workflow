# workflow-pm-wake-summary 2026-04-18 00:04:47

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-a66bbd2b`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- version_transition_decision: `stay(V4)`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `等待 idle watcher 在空窗把 20260417-235555 切进 prod，再复跑 current-version smoke / pm current-version snapshot refresh / workboard jump-strip probe`
- preference_ref: `state/user-preferences.md`
- delta_observation: `pm-main` 这轮同时暴露了 snapshot drift refresh 脏批次和 workboard jump-strip 的并发 dirty；如果只收一半，下一轮 release boundary 会继续挂脏。`
- delta_validation: `prod` 切到 `20260417-235555` 后，优先复跑 `collect_v4_r1_r4_current_version_smoke.py`、`verify_pm_current_version_snapshot_refresh.py` 和 `verify_assignment_workboard_layout_rules.js`。`
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`

## 巡检结论
- `prod` 服务健康，`/healthz.ok=true`。
- `/api/status` 当前为 `running_task_count=1 / queued_task_count=2 / active_version=V4 / lane=工程质量探测 / lifecycle_stage=基于基线测试`。
- `prod` 当前版本仍是 `20260417-220802`，新 `candidate=20260417-235555` 已生成，`candidate_is_newer=true / drain_active=true / running_task_count=1`，当前还不是升级空窗。
- 主线没有断链：enabled patrol 已在 `2026-04-18T00:00:00+08:00` 命中并建出 `queued node=node-sti-20260418-e0f47aaf`，下一次 patrol 仍排在 `2026-04-18T00:20:00+08:00`；enabled mainline 也保留了 `queued node=node-sti-20260417-b825bdb1` 的出口。
- `test` 已切到 `20260417-235555`，我又把部署后冒出来的 ghost running 清到 `running_task_count=0 / ghost_running_detected=false`，测试基线已恢复干净。

## 本轮推进性修改
- 我把上一轮遗留的 snapshot drift refresh 脏批次收口成 `.repository/pm-main@081ecc7 / ../workflow_code@081ecc7`：
  - `scripts/workflow_env_common.ps1` 现在会在 prod restart drift repair 后，对 `refreshResult` 先做 `Get-WorkflowScalarValue` 标量归一，再把 `changed_files` 保持成数组。
  - `scripts/acceptance/verify_pm_current_version_snapshot_refresh.py` 同步补上 watchdog restart drift refresh hook 断言。
- 我把并发浮出来的 workboard jump-strip 批次收口成 `.repository/pm-main@14d21e7 / ../workflow_code@14d21e7`：
  - `assignment_center_render_runtime.js` 为 `协作泳道 / 近期失败池 / 定时入口` 增加 jump strip 和 section anchor。
  - `assignment_center_events.js` 增加 jump chip 点击后的平滑定位。
  - `index_training_loop_panels.css` 补齐 jump strip 样式和 section `scroll-margin-top`。
  - `verify_assignment_workboard_layout_rules.js` 也改成对真实 render-runtime 落点做验收，不再误读 template/events。
- 我按 `test-session-manager` 重跑了 `line budget -> verify_pm_current_version_snapshot_refresh.py -> verify_assignment_workboard_layout_rules.js -> workflow gate`，随后停掉旧 `test` 并重新部署，刷新出新的 `prod candidate=20260417-235555`。
- 这轮推进同时覆盖了 `工程质量探测 + 当前需求开发 + 发布推进`，不是纯巡检。

## 版本评估
- `V4-R1`: `in_progress / 88% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 45% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 50% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `next_activation_ready=false`，`V5` 继续保持 `backlog activation_readiness=draft`，本轮不切版，也没有新增 AAR。

## 证据
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `.repository/pm-main/.test/20260417-234040-800/report.md`
- `.repository/pm-main/.test/20260417-234810-950/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260417-235111.md`
- `.running/control/logs/test/deploy-20260417-235555.json`
- `git -C .repository/pm-main rev-parse HEAD -> 14d21e7`
- `git -C ../workflow_code rev-parse HEAD -> 14d21e7`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8092/api/runtime-upgrade/status`
- `POST http://127.0.0.1:8092/api/runtime-upgrade/repair-ghost-running`

## Next
- 我先等 idle watcher 在空窗把 `candidate=20260417-235555` 切进 `prod`。
- 切版后第一优先复跑 `collect_v4_r1_r4_current_version_smoke.py`、`verify_pm_current_version_snapshot_refresh.py` 和 `verify_assignment_workboard_layout_rules.js`，确认 live `prod` 也吃到这批修复。
- 如果 `235555` live 后仍有红点，我下一轮优先把 `V4-R3` 剩余的 `task-center failure/detail drift` 转成正式 route，不把 release boundary 或 ghost 风险再滚回下一轮。
