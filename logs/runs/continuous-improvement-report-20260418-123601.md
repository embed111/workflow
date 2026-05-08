# Continuous Improvement Report 2026-04-18 12:36:01 +08:00

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260418-407a8557`
- stage: `基于基线测试`
- lane: `工程质量探测`
- preference_ref: `state/user-preferences.md`

## 本轮推进
- 我把 `test` 部署后的 ghost-running 手工 repair 缺口收成了正式发布合同：`scripts/workflow_env_common.ps1` 新增 `Invoke-WorkflowRepairGhostRunningIfDetected`，`scripts/deploy_workflow_env.ps1` 现在会在 `test gate` 通过后自动检测并执行 `/api/runtime-upgrade/repair-ghost-running`。
- 我新增了 `scripts/acceptance/verify_test_deploy_post_ghost_repair.py` 并接入 `workflow gate`，锁住“命中 ghost 自动 repair”和“未命中 ghost 直接 skip”两条合同。
- 代码已提交为 `.repository/pm-main@6290feb`，并已 non-destructive 收口到 `../workflow_code@6290feb`。
- 我重新部署 `test`，刷新出 `prod candidate=20260418-123447`；`deploy-20260418-123447.json` 已记录 `post_deploy_ghost_running.repaired_count=1`，`8092 /api/runtime-upgrade/status` 当前为 `current_version=20260418-123447 / ghost_running_detected=false / running_task_count=0`。

## 验证
- `.repository/pm-main/.test/20260418-122427-873/report.md`
- `.repository/pm-main/.test/20260418-122427-890/report.md`
- `.repository/pm-main/.test/20260418-122851-169/report.md`
- `.repository/pm-main/.test/20260418-122907-860/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-123234.md`
- `.running/control/logs/test/deploy-20260418-123447.json`
- `GET http://127.0.0.1:8092/api/runtime-upgrade/status`
- `GET http://127.0.0.1:8090/api/runtime-upgrade/status`

## 版本判断
- `active_version=V4` 继续保持，`version_transition_decision=stay(V4)`。
- 当前阶段仍是 `基于基线测试`，当前最高价值泳道仍是 `工程质量探测`。
- 需求状态更新：
  - `V4-R1=in_progress / 90% / eta=2026-04-19 / 未超时`
  - `V4-R2=in_progress / 60% / eta=2026-04-20 / 未超时`
  - `V4-R3=in_progress / 95% / eta=2026-04-20 / 未超时`
  - `V4-R4=completed / 100% / eta=2026-04-17 / 未超时`
- 当前不新增 AAR；`V5` 仍保持 `backlog activation_readiness=draft`。

## 发布边界与剩余风险
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=6290feb`
- `push_block_reason=- / next_push_batch=等待 idle watcher 在空窗把 prod 升到 20260418-123447 后，复跑 live current-version smoke / recent-failure contract`
- 当前剩余风险：`prod` 仍在 `20260418-115555` 上有 `running_task_count=1`，所以 `candidate=20260418-123447` 还在等待 idle watcher 创造升级空窗；`test` 侧 ghost repair 已正式自动化，但仍要等 `prod` 实际切版后再确认 live 合同没有回退。

## 增量观察
- delta_observation: `test` 部署后的 `T9` ghost-running 已不再依赖人工补 repair，部署报告里已经能稳定看到 before/after 证据。
- delta_validation: 等 `prod` 切到 `20260418-123447` 后，优先复跑 `collect_v4_r1_r4_current_version_smoke.py` 与 live `recent failure` 合同，并确认 `prod` 不再需要额外手工 ghost repair。
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`
