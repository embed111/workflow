# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260418-9f3ac0b9`
- generated_at: `2026-04-18T17:40:29+08:00`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`

## 本轮推进
- 我把 `prod-idle-upgrade-watchdog` 的历史 `apply_wait_seconds` 参数漂移收成 `.repository/pm-main@e194b05 / ../workflow_code@e194b05`：`apply_prod_candidate_when_idle.py` 现在会对旧 supervisor 传入的过小 wait 值自动钳到 `600s`，并在日志里写出校正提示。
- 我同步给 `verify_apply_prod_candidate_when_idle.py` 增加 `legacy_watchdog_apply_wait_clamp` probe，锁住“旧 caller 传 `420s` 也会按 `600s` 工作”的回归。
- 我跑通了 `line budget`、`verify_apply_prod_candidate_when_idle.py`、`verify_prod_auto_upgrade_single_check_helper.py` 和完整 `workflow gate`，随后刷新出 `test / prod candidate=20260418-173831`，并把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate / pm-main` 全部拉回 `clean_synced@e194b05`。

## Live 真相
- `2026-04-18 17:40:29 +08:00` 的 `prod` 仍是 `current_version=20260418-165853`，新的 `candidate_version=20260418-173831` 已生成；当前 `running_task_count=1 / drain_active=true / can_upgrade=false`，所以正式升级还在等 idle watcher 的空窗。
- `2026-04-18 17:15:01 +08:00` 的 live 日志已经证明旧 supervisor 会把历史较小 wait 值传给 watcher：`prod` 实际在 `2026-04-18 17:23:02 +08:00` 升到 `165853`，但旧日志先在 `2026-04-18 17:22:04 +08:00` 写了超时。我这轮修的是这条兼容缺口，不再把效果绑在 supervisor 重启时机上。
- 当前发布边界为 `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=e194b05`。`git -C .repository/pm-main status --short --branch` 的 `ahead 1` 只指向 GitHub tracking 参考，不构成本机 `workspace -> ../workflow_code` 阻塞。

## 版本评估
- `V4-R1`: `in_progress / 90% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 99% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `version_transition_decision=stay(V4)`；`next_activation_ready=false`，`V5` 仍是 `backlog activation_readiness=draft`。本轮无 AAR。

## 验证
- `python scripts/quality/check_workspace_line_budget.py --root .`
- `python scripts/acceptance/verify_apply_prod_candidate_when_idle.py`
- `python scripts/acceptance/verify_prod_auto_upgrade_single_check_helper.py`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/stop_workflow_env.ps1 -Environment test`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/deploy_test_workflow_env.ps1`
- `python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod status`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/schedules`

## 关键产物
- `.repository/pm-main/scripts/apply_prod_candidate_when_idle.py`
- `.repository/pm-main/scripts/acceptance/verify_apply_prod_candidate_when_idle.py`
- `.running/control/logs/test/deploy-20260418-173831.json`
- `.repository/pm-main/.test/20260418-173139-828/report.md`
- `.repository/pm-main/.test/20260418-173203-959/report.md`
- `.repository/pm-main/.test/20260418-173233-394/report.md`
- `.repository/pm-main/.test/20260418-173243-824/report.md`
- `pm/PM当前版本计划.md`
- `pm/versions/V4/版本计划.md`
- `pm/versions/V4/history/2026-04/2026-04-18.md`
- `.codex/memory/2026-04/2026-04-18.md`

## 下一步
- 等 `prod` 空窗让 idle watcher 把 `20260418-173831` 切进 live。
- 切版后第一优先复核 `logs/runs/prod-idle-upgrade-watchdog-live.md`，确认 watcher 在旧 supervisor 仍传历史 wait 值时也不会提前写超时。
- 下一条 mainline 目前是 `node-sti-20260418-fb1d611d`（命中时间 `2026-04-18T17:28:00+08:00`，当前 `ready`）；保底巡检当前到时点是 `2026-04-18T17:40:00+08:00`，由系统继续建单和派发。

- preference_ref: `state/user-preferences.md`
- delta_observation: 我确认 `prod` supervisor `20500` 是 `2026-04-17 09:14:37 +08:00` 启动的旧进程，会继续显式传历史 wait 值给新 watcher；Python 侧兼容兜底比单等 supervisor 重启更稳。
- delta_validation: 等 `20260418-173831` live 后，复核 `prod-idle-upgrade-watchdog-live.md` 是否出现 apply-wait 校正日志且不再提前超时。
