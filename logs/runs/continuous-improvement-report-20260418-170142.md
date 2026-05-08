# Continuous Improvement Report

- generated_at: `2026-04-18T17:01:42+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260418-29e86396`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- version_transition_decision: `stay(V4)`
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`
- preference_ref: `state/user-preferences.md`
- delta_observation: `prod` idle watcher 在升级重连窗口里会连续刷相同的 `request_failed`；这类重复噪声已经值得进入正式 probe 与版本化治理，而不是继续留在 live 日志里扩散。
- delta_validation: `candidate=20260418-165853` 切进 `prod` 后，复核 `logs/runs/prod-idle-upgrade-watchdog-live.md` 是否已经按新合同只保留首条 unavailable 错误并补恢复摘要。

## 本轮推进

- 我把 `prod` idle watcher 在升级重连窗口里的重复 `request_failed` 日志噪声收成 `.repository/pm-main@36f812f / ../workflow_code@36f812f`：`apply_prod_candidate_when_idle.py` 现在对连续相同的 unavailable 只保留首条原始错误，状态恢复后再补一条累计摘要。
- 我给 `verify_apply_prod_candidate_when_idle.py` 新增了 `upgrade_wait_unavailable_log_compaction` probe，并保住了现有 `single_check / slow-repair settle` 合同；`verify_prod_auto_upgrade_single_check_helper.py` 继续转绿。
- 我按 `test-session-manager` 跑通了 `line budget`、watcher 定向 probe、PowerShell helper probe 和完整 `workflow gate`，然后把代码提交成 `36f812f fix(runtime-upgrade): 压缩升级等待阶段重复状态错误日志`。
- 我把本机 `../workflow_code` fast-forward 到 `36f812f`，执行 `stop_test_workflow_env.ps1 + deploy_test_workflow_env.ps1` 刷新出 `test / prod candidate=20260418-165853`。
- 我把 `pm-main + 5` 个 helper developer workspace 全部 refresh 到 `clean_synced@36f812f`，没有把新的 workspace drift 留给下一轮。

## 当前真相

- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=36f812f`
- `manage_developer_workspace.py --root .running/control/runtime/prod status` 当前返回 `developer_workspace_count=6 / clean_synced=6`
- `prod` 当前仍是 `20260418-161644`，`candidate=20260418-165853`，`candidate_is_newer=true / drain_active=true / running_task_count=1 / ghost_running_detected=false`
- `test` 当前已是 `20260418-165853`，`candidate_is_newer=false / running_task_count=0 / ghost_running_detected=false`
- `V4-R1=90% / eta=2026-04-19 / 未超时`
- `V4-R2=60% / eta=2026-04-20 / 未超时`
- `V4-R3=99% / eta=2026-04-20 / 未超时`
- `V4-R4=100% / eta=2026-04-17 / 未超时`

## 验证

- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `.repository/pm-main/.test/20260418-165248-225/report.md`
- `.repository/pm-main/.test/20260418-165320-543/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-165709.md`
- `.running/control/logs/test/deploy-20260418-165853.json`
- `python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod status`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`

## 下一步

- 等 idle watcher 在空窗把 `candidate=20260418-165853` 切进 `prod`。
- 切版后第一优先复核 `logs/runs/prod-idle-upgrade-watchdog-live.md`，确认 live watcher 在升级重连窗口里只保留首条 unavailable 错误并补恢复摘要。
- 如果 `165853` live 后还有红点，下一轮继续沿 `V4-R3` 的 formal route 往下切，不回到纯观察。
